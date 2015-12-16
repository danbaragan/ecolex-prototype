TREATY = 'treaty'
COP_DECISION = 'decision'
COURT_DECISION = 'court_decision'
LITERATURE = 'literature'
LEGISLATION = 'legislation'

DOC_TYPE = (
    (TREATY, "Treaty"),
    (COP_DECISION, "Decision"),
    (LITERATURE, "Literature"),
    (COURT_DECISION, "Court Decision"),
    (LEGISLATION, "Legislation"),
)

DOC_SOURCES = {
    TREATY: 'IUCN',
    COP_DECISION: 'InforMEA',
    LITERATURE: 'IUCN',
    COURT_DECISION: 'InforMEA',
    LEGISLATION: 'FAO',
}

TREATY_FILTERS = {
    'trTypeOfText_en': 'tr_type',
    'trFieldOfApplication_en': 'tr_field',
    'trStatus': 'tr_status',
    'trPlaceOfAdoption': 'tr_place_of_adoption',
    'trDepository_en': 'tr_depository',
}

DECISION_FILTERS = {
    'decType': 'dec_type',
    'decStatus': 'dec_status',
    'decTreatyId': 'dec_treaty',
}

LITERATURE_FILTERS = {
    'litTypeOfText': 'lit_type',
    'litAuthor': 'lit_author',
    'litSerialTitle': 'lit_serial',
    'litPublisher': 'lit_publisher',
}

COURT_DECISION_FILTERS = {
    'cdTerritorialSubdivision': 'cd_territorial_subdivision',
    'cdTypeOfText': 'cd_type',
}

LEGISLATION_FILTERS = {
    'legType_en': 'leg_type',
    'legTerritorialSubdivision': 'leg_territorial',
    'legStatus': 'leg_status',
}

DOC_TYPE_FILTER_MAPPING = {
    TREATY: TREATY_FILTERS,
    COP_DECISION: DECISION_FILTERS,
    LITERATURE: LITERATURE_FILTERS,
    COURT_DECISION: COURT_DECISION_FILTERS,
    LEGISLATION: LEGISLATION_FILTERS,
}

FIELD_TO_FACET_MAPPING = {
    'tr_type': 'trTypeOfText_en',
    'tr_field': 'trFieldOfApplication_en',
    'tr_status': 'trStatus',
    'tr_place_of_adoption': 'trPlaceOfAdoption',
    'tr_depository': 'trDepository_en',

    'dec_type': 'decType',
    'dec_status': 'decStatus',
    'dec_treaty': 'decTreatyId',

    'lit_type': 'litTypeOfText',
    'lit_author': 'litAuthor',
    'lit_serial': 'litSerialTitle',
    'lit_publisher': 'litPublisher',

    'cd_territorial_subdivision': 'cdTerritorialSubdivision',
    'cd_type': 'cdTypeOfText',

    'leg_type': 'legType_en',
    'leg_territorial': 'legTerritorialSubdivision',
    'leg_status': 'legStatus',

    'subject': 'docSubject',
    'keyword': 'docKeyword',
    'country': 'docCountry',
    'region': 'docRegion',
    'language': 'docLanguage',
}


OPERATION_FIELD_MAPPING = {
    'tr_depository_op': 'tr_depository',
    'lit_author_op': 'lit_author',
    'subject_op': 'subject',
    'keyword_op': 'keyword',
    'country_op': 'country',
    'region_op': 'region',
    'language_op': 'language',
}

FIELDS_BY_TYPE = {
    TREATY: [
        'id', 'type', 'source', 'trTitleOfText', 'trJurisdiction',
        'trStatus', 'trPlaceOfAdoption', 'trDateOfText', 'trDateOfEntry',
        'trDateOfModification', 'trPaperTitleOfText', 'trPaperTitleOfTextFr',
    ],
    COP_DECISION: [
        'id', 'type', 'source', 'decTitleOfText', 'decStatus', 'decPublishDate',
        'decUpdateDate', 'decNumber',
    ],
    LITERATURE: [
        'id', 'type', 'source',
        'litLongTitle', 'litLongTitle_fr', 'litLongTitle_sp',
        'litLongTitle_other',
        'litPaperTitleOfText', 'litPaperTitleOfText_fr',
        'litPaperTitleOfText_sp',
        'litPaperTitleOfText_other',
        'litTitleOfTextShort', 'litTitleOfTextShort_fr',
        'litTitleOfTextShort_sp',
        'litTitleOfTextShort_other',
        'litTitleOfTextTransl', 'litTitleOfTextTransl_fr',
        'litTitleOfTextTransl_sp',
        'litDateOfEntry', 'litDateOfModifcation', 'litAbstract',
        'litTypeOfText',
        'litScope', 'litScope_fr', 'litScope_sp',
        'litAuthor', 'litCorpAuthor',
        'litPublisher', 'litPublPlace', 'litDateOfText',
        'litKeyword', 'litSeriesFlag',
        'litCountry', 'litRegion', 'litSubject', 'litLanguageOfDocument',
    ],
    COURT_DECISION: [
        'id', 'type', 'source',
        'cdTitleOfText',
        'cdAbstract',
        'cdAlternativeRecordId',
        'cdSeatOfCourt',
        'cdCountry',
        'cdCourtDecisionIdNumber',
        'cdCourtDecisionSubdivision',
        'cdCourtName',
        'cdDateOfEntry',
        'cdDateOfModification',
        'cdStatusOfDecision',
        'cdSubject',
        'cdEcolexUrl',
        'cdFaolexUrl',
        'cdFiles',
        'cdInformeaTags',
        'cdInternetReference',
        'cdIsisNumber',
        'cdJurisdiction',
        'cdJustices',
        'cdNumberOfPages',
        'cdOriginalId',
        'cdReferenceNumber',
        'cdReferenceToLegislation',
        'cdRelatedUrl',
        'cdLanguageOfDocument',
        'cdTerritorialSubdivision',
        'cdTypeOfText',
        'cdLinkToFullText',
        'cdNotes',
        'cdAbstractOther',
        'cdAvailableIn',
        'cdCourtDecisionReference',
        'cdKeywords',
        'cdFaolexReference',
        'cdInstance',
        'cdOfficialPublication',
        'cdRegion',
        'cdTitleOfTextOther',
        'cdTitleOfTextShort',
        'cdTreatyReference',
        'cdUrlOther',
        'cdDateOfText',
    ],
    LEGISLATION: [
        'id', 'type', 'source',
        'legTitle', 'legLongTitle', 'legCountry_en',
        'legDate', 'legStatus', 'legTerritorialSubdivision',
    ],
}

SOLR_FIELDS = [
    'id', 'type', 'source', 'trTitleOfText', 'trJurisdiction_en', 'trStatus',
    'trPlaceOfAdoption', 'trDateOfText', 'trDateOfEntry',
    'trDateOfModification', 'trPaperTitleOfText_en', 'trPaperTitleOfText_fr',
    'trPaperTitleOfText_sp', 'trPaperTitleOfText_other', 'trTitleOfTextShort',
    'decTitleOfText', 'decStatus', 'decPublishDate', 'decUpdateDate',
    'decNumber',
    'litLongTitle', 'litLongTitle_fr', 'litLongTitle_sp', 'litLongTitle_other',
    'litPaperTitleOfText', 'litPaperTitleOfText_fr', 'litPaperTitleOfText_sp',
    'litPaperTitleOfText_other',
    'litTitleOfTextShort', 'litTitleOfTextShort_fr', 'litTitleOfTextShort_sp',
    'litTitleOfTextShort_other',
    'litTitleOfTextTransl', 'litTitleOfTextTransl_fr',
    'litTitleOfTextTransl_sp',
    'litDateOfEntry', 'litDateOfModifcation', 'litAbstract',
    'litTypeOfText',
    'litScope', 'litScope_fr', 'litScope_sp',
    'litAuthor', 'litCorpAuthor',
    'litPublisher', 'litPublPlace', 'litDateOfText',
    'litKeyword', 'litSeriesFlag',
    'litCountry', 'litRegion', 'litSubject', 'litLanguageOfDocument',
    'decNumber', 'cdTitleOfText_en', 'cdTitleOfText_es', 'cdTitleOfText_fr',
    'cdDateOfText', 'legTitle', 'legLongTitle', 'legCountry_en',
    'legDate', 'legStatus', 'legTerritorialSubdivision'
]

LANGUAGE_MAP = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'ru': 'Russian',
}
