import json
import logging
import logging.config
import tempfile
from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict
from pysolr import SolrError

from django.conf import settings
from django.template.defaultfilters import slugify

from ecolex.management.commands.logging import LOG_DICT
from ecolex.management.definitions import LEGISLATION
from ecolex.management.utils import EcolexSolr
from ecolex.models import DocumentText

logging.config.dictConfig(LOG_DICT)
logger = logging.getLogger('legislation_import')

DOCUMENT = 'record'
META = 'meta'
CONTENT = 'content'
REPEALED = 'repealed'
IN_FORCE = 'in force'

FIELD_MAP = {
    'id': 'legId',
    'faolexId': 'legId',
    'titleOfText': 'legTitle',
    'longTitleOfText': 'legLongTitle',
    'serialImprint': 'legSource',

    'year': 'legYear',
    'originalYear': 'legOriginalYear',

    'entryIntoForce': 'legEntryIntoForce',
    'country_ISO3': 'legCountry_iso',
    'country_en': 'legCountry_en',
    'country_fr': 'legCountry_fr',
    'country_es': 'legCountry_es',
    'territorialSubdivision_en': 'legTerritorialSubdivision',
    'geographicalArea_en': 'legGeoArea_en',
    'geographicalArea_fr': 'legGeoArea_fr',
    'geographicalArea_es': 'legGeoArea_es',
    'basin_en': 'legBasin_en',
    'basin_fr': 'legBasin_fr',
    'basin_es': 'legBasin_es',

    'typeOfTextCode': 'legTypeCode',
    'typeOfText_en': 'legType_en',
    'typeOfText_fr': 'legType_fr',
    'typeOfText_es': 'legType_es',

    'relatedWebSite': 'legRelatedWebSite',
    'recordLanguage': 'legLanguage_code',
    'documentLanguage_en': 'legLanguage_en',

    'textAbstract': 'legAbstract',
    'abstract': 'legAbstract',
    'subjectSelectionCode': 'legSubject_code',
    'subjectSelection_en': 'legSubject_en',
    'subjectSelection_fr': 'legSubject_fr',
    'subjectSelection_es': 'legSubject_es',
    'keywordCode': 'legKeyword_code',
    'keyword_en': 'legKeyword_en',
    'keyword_fr': 'legKeyword_fr',
    'keyword_es': 'legKeyword_es',

    'implement': 'legImplement',
    'amends': 'legAmends',
    'repeals': 'legRepeals',

    'implementsTre': 'legImplementTreaty',
    'citesTre': 'legCitesTreaty',
}

MULTIVALUED_FIELDS = [
    'legLanguage_en',
    'legKeyword_code', 'legKeyword_en', 'legKeyword_fr', 'legKeyword_es',
    'legGeoArea_en', 'legGeoArea_fr', 'legGeoArea_es',
    'legBasin_en', 'legBasin_fr', 'legBasin_es',
    'legImplement', 'legAmends', 'legRepeals', 'legImplementTreaty',
    'legCitesTreaty',
    'legSubject_code', 'legSubject_en', 'legSubject_fr', 'legSubject_es',
]

LANGUAGE_FIELDS = ['legLanguage_en', 'legLanguage_fr', 'legLanguage_es']


def get_content(values):
    values = [v.get(CONTENT, None) for v in values]
    return values


def harvest_file(upfile):
    if settings.DEBUG:
        with tempfile.NamedTemporaryFile(prefix=upfile.name, delete=False) as f:
            logger.debug('Dumping data to %s' % (f.name))
            for chunk in upfile.chunks():
                f.write(chunk)
            upfile.seek(0)

    bs = BeautifulSoup(upfile)
    documents = bs.findAll(DOCUMENT)
    legislations = []
    count_ignored = 0

    with open(settings.SOLR_IMPORT['common']['regions_json']) as f:
        json_regions = json.load(f)

    with open(settings.SOLR_IMPORT['common']['keywords_json']) as f:
        json_keywords = json.load(f)

    with open(settings.SOLR_IMPORT['common']['subjects_json']) as f:
        json_subjects = json.load(f)

    with open(settings.SOLR_IMPORT['common']['fao_countries_json'], encoding='utf-8') as f:
        json_countries = json.load(f)

    with open(settings.SOLR_IMPORT['common']['languages_json']) as f:
        languages_codes = json.load(f)

    all_languages = {}
    for k, v in languages_codes.items():
        key = v['en'].lower()
        all_languages[key] = v
        if 'en2' in v:
            key = v['en2'].lower()
            all_languages[key] = v

    for document in documents:
        legislation = {
            'type': LEGISLATION,
            'legLanguage_es': set(),
            'legLanguage_fr': set(),
        }

        for k, v in FIELD_MAP.items():
            field_values = get_content(document.findAll(META, {'name': k}))

            if field_values and v not in MULTIVALUED_FIELDS:
                field_values = field_values[0]

            # if v in DATE_FIELDS and field_values:
            #    field_values = get_date_format(field_values)

            if field_values:
                legislation[v] = field_values

        #  remove duplicates
        for field_name in MULTIVALUED_FIELDS:
            field_values = legislation.get(field_name)
            if field_values:
                legislation[field_name] = list(
                    OrderedDict.fromkeys(field_values).keys())

        langs = legislation.get('legLanguage_en', [])
        legislation['legLanguage_en'] = set()
        for lang in langs:
            key = lang.lower()
            if key in all_languages:
                for lang_field in LANGUAGE_FIELDS:
                    legislation[lang_field].add(all_languages[key][lang_field[-2:]])
            else:
                for lang_field in LANGUAGE_FIELDS:
                    legislation[lang_field].add(lang)
                logger.error('Language not found %s' % (lang))

        for lang_field in LANGUAGE_FIELDS:
            legislation[lang_field] = list(legislation[lang_field])

        if ('legTypeCode' in legislation):
            if legislation['legTypeCode'] == 'A':
                # Ignore International agreements
                logger.debug('Ignoring {}'.format(legislation.get('legId')))
                count_ignored += 1
                continue

        _set_values_from_dict(legislation, 'legGeoArea', json_regions)
        _set_values_from_dict(legislation, 'legSubject', json_subjects)
        _set_values_from_dict(legislation, 'legKeyword', json_keywords)

        # overwrite countries with names from the dictionary
        iso_country = legislation.get('legCountry_iso')
        if iso_country:
            fao_country = json_countries.get(iso_country)
            if fao_country:
                legislation['legCountry_en'] = fao_country.get('en')
                legislation['legCountry_es'] = fao_country.get('es')
                legislation['legCountry_fr'] = fao_country.get('fr')

        legYear = legislation.get('legYear')
        if legYear:
            try:
                legDate = datetime.strptime(legYear, '%Y')
                legislation['legDate'] = legDate.strftime('%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                logger.debug('Error parsing legYear %s' % (legYear))

        url_value = document.attrs.get('url', None)
        if url_value:
            legislation['legLinkToFullText'] = url_value

        if (REPEALED.upper() in
                get_content(document.findAll(META, {'name': REPEALED}))):
            legislation['legStatus'] = REPEALED
        else:
            legislation['legStatus'] = IN_FORCE

        treaties = legislation.get('legImplementTreaty', [])
        cleaned_treaties = []
        for treaty in treaties:
            if treaty.endswith('.pdf'):
                treaty = treaty[:-4]
            cleaned_treaties.append(treaty)
        legislation['legImplementTreaty'] = cleaned_treaties

        title = legislation.get('legTitle') or legislation.get('legLongTitle')
        slug = title + ' ' + legislation.get('legId')
        legislation['slug'] = slugify(slug)

        legislations.append(legislation)

    response = add_legislations(legislations, count_ignored)
    return response


def add_legislations(legislations, count_ignored):
    solr = EcolexSolr()
    new_docs = []
    updated_docs = []
    new_legislations = []
    updated_legislations = []
    failed_docs = []

    for legislation in legislations:
        leg_id = legislation.get('legId')
        doc, _ = DocumentText.objects.get_or_create(doc_id=leg_id)
        doc.doc_type = LEGISLATION
        doc.status = DocumentText.INDEX_FAIL
        try:
            leg_result = solr.search(LEGISLATION, leg_id)
            if leg_result:
                legislation['updatedDate'] = (datetime.now()
                                              .strftime('%Y-%m-%dT%H:%M:%SZ'))
                legislation['id'] = leg_result['id']
                updated_legislations.append(legislation)
                updated_docs.append(doc)
            else:
                new_legislations.append(legislation)
                new_docs.append(doc)
        except SolrError as e:
            logger.error('Error importing legislation %s' % (leg_id,))
            failed_docs.append(doc)
            if settings.DEBUG:
                logger.exception(e)

        doc.parsed_data = json.dumps(legislation)
        if (doc.url != legislation['legLinkToFullText']):
            doc.url = legislation['legLinkToFullText']
            # will not re-parse if same url and doc_size
            doc.doc_size = None

    # Mix of exceptions and True/False return status
    # hoping that add_bulk has better performance than add
    count_new = index_and_log(solr, new_legislations, new_docs)
    count_updated = index_and_log(solr, updated_legislations, updated_docs)
    for doc in new_docs + updated_docs + failed_docs:
        doc.save()

    response = 'Total %d. Added %d. Updated %d. Failed %d. Ignored %d' % (
        len(legislations) + count_ignored,
        count_new,
        count_updated,
        len(legislations) - count_new - count_updated,
        count_ignored
    )
    return response


def _set_values_from_dict(data, field, local_dict):
    id_field = 'legId'
    langs = ['en', 'fr', 'es']
    fields = ['{}_{}'.format(field, lang_code) for lang_code in langs]
    new_values = {x: [] for x in langs}
    if all(map((lambda x: x in data), fields)):
        values = zip(*[data[x] for x in fields])
        for val_en, val_fr, val_es in values:
            dict_values = local_dict.get(val_en.lower())
            if dict_values:
                new_values['en'].append(dict_values['en'])
                dict_value_fr = dict_values['fr']
                dict_value_es = dict_values['es']
                if val_fr != dict_value_fr:
                    logger.debug('{}_fr name different: {} {} {}'.format(
                                 field, data[id_field], val_fr,
                                 dict_value_fr))
                new_values['fr'].append(dict_value_fr)
                if val_es != dict_value_es:
                    logger.debug('{}_es name different: {} {} {}'.format(
                                 field, data[id_field], val_es,
                                 dict_value_es))
                new_values['es'].append(dict_value_es)
            else:
                logger.warning('New {} name: {} {} {} {}'.format(
                               field, data[id_field], val_en,
                               val_fr, val_es))
                new_values['en'].append(val_en)
                new_values['fr'].append(val_fr)
                new_values['es'].append(val_es)
    elif fields[0] in data:
        values_en = data.get(fields[0], []) or []
        for val_en in values_en:
            dict_values = local_dict.get(val_en.lower())
            if dict_values:
                for lang in langs:
                    new_values[lang].append(dict_values[lang])
            else:
                logger.warning('New {}_en name: {} {}'.format(
                               field, data[id_field], val_en))
                new_values['en'].append(val_en)
    for field in fields:
        data[field] = new_values[field[-2:]]


def index_and_log(solr, legislations, docs):
    # solr.add_bulk returns False on fail
    faolex_enabled = getattr(settings, 'FAOLEX_ENABLED', False)
    if faolex_enabled:
        if not solr.add_bulk(legislations):
            return 0
        for doc in docs:
            doc.status = DocumentText.INDEXED
            # no need to store what is already indexed in Solr
            doc.parsed_data = ''
    return len(legislations)
