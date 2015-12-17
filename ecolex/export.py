from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from ecolex.definitions import DOC_TYPE, FIELDS_BY_TYPE


def get_exporter(format):
    exporters = {
        'xls': ExcelExporter,
        'xml': XMLExporter,
    }
    return exporters.get(format)


class Exporter(object):
    DATE_FORMAT = '%Y%m%d'

    def __init__(self, results):
        self.documents = results

    def get_data(self):
        raise NotImplementedError

    def get_filename(self):
        current_date = date.today().strftime(self.DATE_FORMAT)
        filename = 'ecolex_{}.{}'.format(current_date, self.EXTENSION)
        return filename

    def get_response(self, download=True):
        data = self.get_data()
        filename = self.get_filename()

        resp = HttpResponse(data, content_type=self.CONTENT_TYPE)
        if download:
            content_disposition = 'attachment; filename="{}"'.format(filename)
            resp['Content-Disposition'] = content_disposition

        return resp


class ExcelExporter(Exporter):
    CONTENT_TYPE = 'application/vnd.ms-excel'
    EXTENSION = 'xls'

    def _get_workbook(self):
        sheet_names = dict(DOC_TYPE)
        wb = Workbook()
        wb.remove_sheet(wb.active)

        for document in self.documents:
            doc_type = document.type
            sheet_title = sheet_names[doc_type]
            fields = FIELDS_BY_TYPE[doc_type]

            if sheet_title not in wb:
                sheet = wb.create_sheet(sheet_title)
                sheet.append(fields)

            sheet = wb[sheet_title]
            sheet.append([document.get_str(field) for field in fields])

        return wb

    def get_data(self):
        wb = self._get_workbook()
        data = save_virtual_workbook(wb)
        return data


class XMLExporter(Exporter):
    CONTENT_TYPE = 'text/xml'
    EXTENSION = 'xml'
    TEMPLATE_NAME = 'exports/base.xml'

    def get_data(self):
        data = render_to_string(self.TEMPLATE_NAME,
                                {'documents': self.documents})
        return data
