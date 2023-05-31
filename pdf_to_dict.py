import PyPDF2
from bar_code_reader import ReadBarCodes


'''
I assume that pdfs should always be in the same format 
and I basically just need to extract data from it in a computer-readable format;
'''


class ValidatePDF:
    def __init__(self, pdf_path: str):
        reader = PyPDF2.PdfReader(pdf_path)
        self.text = reader.pages[0].extract_text()
        self.result_dict = {
            'name': None, 'long barcode': None, 'PN': None, 'SN': None, 'DESCRIPTION': None, 'LOCATION': None,
            'CONDITION': None, 'RECEIVER#': None, 'UOM': None, 'EXP DATE': None, 'PO': None,
            'CERT SOURCE': None, 'REC.DATE': None, 'MFG': None, 'BATCH#': None, 'DOM': None,
            'REMARK': None, 'LOT#': None, 'TAGGED BY': None, 'Qty': None, 'NOTES': None
        }
        self.indices_dict = {}
        self.populate_result_dict()

    def list_of_lines(self) -> list:
        return self.text.split('\n')

    def populate_result_dict(self) -> None:
        """Return dict populated with values from PDF"""
        # populate paired values first
        self._populate_result_dict_with_paired_values()

        # populate the only unpaired value
        self._populate_name()

        # populate bar codes
        self._populate_bar_codes()

        # swap empty spaces for None values
        self._replace_empty_values()

    @staticmethod
    def _clean_value(value_to_clean: str, name_of_key_to_remove: str) -> str:
        """
        Remove new lines, semicolons, empty spaces, and other ugly staff from values.
        """
        return value_to_clean.replace(name_of_key_to_remove, '').replace('\n', '').replace(':', '').strip()

    @staticmethod
    def _get_key_by_index(dictionary: dict, key_index: int) -> str:
        """
        Return dict key by index.
        Ex:
        dict1 = {'key1': True, 'key2': False}
        _get_key_by_index(dict1, 1) >>> 'key2'
        """
        return list(dictionary.keys())[key_index]

    def _find_first_indices(self) -> None:
        """
        Populate indices_dict with indexes marking locations of the first char
        of result_dict keys in text.
        Ex: letter 'P' in 'PN' has index 123 in 'self.text',
        letter 'S' in 'SN' has index 143 in 'self.text' because it comes later.
        """
        for key in self.result_dict:
            self.indices_dict[key] = self.text.find(key)

    @staticmethod
    def _get_range(dict_to_get_range_of: dict) -> range:
        """Get range of dict"""
        return range(len(dict_to_get_range_of))

    def _populate_name(self) -> None:
        self.result_dict['name'] = self.list_of_lines()[0]

    def _populate_bar_codes(self) -> None:
        """Assign bar code values to self.result_dict"""
        bar_codes = ReadBarCodes('flight-ticket-or-something.pdf')
        bar_code_values = bar_codes.get_data_from_bar_codes()

        self.result_dict['long barcode'] = bar_code_values['long barcode']
        self.result_dict['TAGGED BY'] = bar_code_values['TAGGED BY']

    def _replace_empty_values(self) -> None:
        """Swap empty spaces for None values"""
        for key, value in self.result_dict.items():
            if value == '':
                self.result_dict[key] = None

    def _populate_result_dict_with_paired_values(self) -> None:
        """
        Populate results dict with values except for bar codes and name

        Ex:
        '...LOCATION: 111 CONDITION: FN...'

        L = start_index (LOCATION)
        C = end_index (CONDITION)

        *slice*
        -> 'LOCATION: 111'

        *remove unnecessary data*
        ('LOCATION', ' ', ':')

        -> '111'

        *populate*
        self.result_dictionary['LOCATION'] = '111'
        """
        # find indexes of first letters of keys in text
        self._find_first_indices()

        # if last index not found, use end of text as last index
        end_index_for_last_item = len(self.text)

        for index in self._get_range(self.indices_dict):

            # get key of the first item
            start_key = self._get_key_by_index(self.indices_dict, index)

            # assign indices
            start_index = self.indices_dict[start_key]
            end_index = None

            # if not last item, get key of the next item
            try:
                next_item_key = self._get_key_by_index(self.indices_dict, index + 1)

                # assign end index if applicable
                end_index = self.indices_dict[next_item_key]
            except IndexError:
                next_item_key = None

            # if index is not -1
            if self.indices_dict[start_key] != '-1':

                # populate ordinary keys
                if next_item_key is not None:
                    cleaned_value = self._clean_value(
                        value_to_clean=self.text[start_index:end_index],
                        name_of_key_to_remove=start_key
                    )
                    self.result_dict[start_key] = cleaned_value

                # populate the last key
                else:
                    cleaned_value = self._clean_value(
                        value_to_clean=self.text[start_index:end_index_for_last_item],
                        name_of_key_to_remove=start_key
                    )
                    self.result_dict[start_key] = cleaned_value
