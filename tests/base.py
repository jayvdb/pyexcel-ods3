import os
import pyexcel
import datetime
from nose.tools import raises


def create_sample_file1(file):
    data=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 1.1, 1]
    table = []
    table.append(data[:4])
    table.append(data[4:8])
    table.append(data[8:12])
    pyexcel.save_as(array=table, dest_file_name=file)


class PyexcelHatWriterBase:
    """
    Abstract functional test for hat writers
    """
    content = {
        "X": [1,2,3,4,5],
        "Y": [6,7,8,9,10],
        "Z": [11,12,13,14,15],
    }
    
    def test_series_table(self):
        pyexcel.save_as(adict=self.content, dest_file_name=self.testfile)
        r = pyexcel.get_sheet(file_name=self.testfile, name_columns_by_row=0)
        actual = pyexcel.utils.to_dict(r)
        assert actual == self.content
    

class PyexcelWriterBase:
    """
    Abstract functional test for writers

    testfile and testfile2 have to be initialized before
    it is used for testing
    """
    content = [
        [1,2,3,4,5],
        [1,2,3,4,5],
        [1,2,3,4,5],
        [1,2,3,4,5]
    ]

    def _create_a_file(self, file):
        pyexcel.save_as(dest_file_name=file,array=self.content)
    
    def test_write_array(self):
        self._create_a_file(self.testfile)
        r = pyexcel.get_sheet(file_name=self.testfile)
        actual = pyexcel.utils.to_array(r.rows())
        assert actual == self.content


class PyexcelMultipleSheetBase:

    def _write_test_file(self, filename):
        pyexcel.save_book_as(bookdict=self.content, dest_file_name=filename)

    def _clean_up(self):
        if os.path.exists(self.testfile2):
            os.unlink(self.testfile2)
        if os.path.exists(self.testfile):
            os.unlink(self.testfile)

    def test_sheet_names(self):
        r = pyexcel.BookReader( self.testfile)
        expected = [ "Sheet1", "Sheet2", "Sheet3"]
        sheet_names = r.sheet_names()
        for name in sheet_names:
            assert name in expected

    def test_reading_through_sheets(self):
        b = pyexcel.BookReader(self.testfile)
        data = pyexcel.utils.to_array(b["Sheet1"].rows())
        expected = [[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]
        assert data == expected
        data = pyexcel.utils.to_array(b["Sheet2"].rows())
        expected = [[4, 4, 4, 4], [5, 5, 5, 5], [6, 6, 6, 6]]
        assert data == expected
        data = pyexcel.utils.to_array(b["Sheet3"].rows())
        expected = [[u'X', u'Y', u'Z'], [1, 4, 7], [2, 5, 8], [3, 6, 9]]
        assert data == expected
        sheet3 = b["Sheet3"]
        sheet3.name_columns_by_row(0)
        data = pyexcel.utils.to_array(b["Sheet3"].rows())
        expected = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        assert data == expected

    def test_iterate_through_sheets(self):
        b = pyexcel.BookReader(self.testfile)
        for s in b:
            data = pyexcel.utils.to_array(s)
            assert self.content[s.name] == data
        si = pyexcel.iterators.SheetIterator(b)
        for s in si:
            data = pyexcel.utils.to_array(s)
            assert self.content[s.name] == data

    def test_random_access_operator(self):
        r = pyexcel.BookReader(self.testfile)
        value = r["Sheet1"][0,1]
        assert value == 1
        value = r["Sheet3"][0,1]
        assert value == 'Y'
        r["Sheet3"].name_columns_by_row(0)
        assert r["Sheet3"][0,1] == 4


class ODSCellTypes:

    def test_formats(self):
        # date formats
        date_format = "%d/%m/%Y"
        assert self.data["Sheet1"][0][0] == "Date"
        assert self.data["Sheet1"][1][0].strftime(date_format) == "11/11/2014"
        assert self.data["Sheet1"][2][0].strftime(date_format) == "01/01/2001"
        assert self.data["Sheet1"][3][0] == ""
        # time formats
        time_format = "%S:%M:%H"
        assert self.data["Sheet1"][0][1] == "Time"
        assert self.data["Sheet1"][1][1].strftime(time_format) == "12:12:11"
        assert self.data["Sheet1"][2][1].strftime(time_format) == "12:00:00"
        assert self.data["Sheet1"][3][1] == 0
        assert self.data["Sheet1"][4][1] == datetime.timedelta(hours=27, minutes=17, seconds=54)
        assert self.data["Sheet1"][5][1] == "Other"
        # boolean
        assert self.data["Sheet1"][0][2] == "Boolean"
        assert self.data["Sheet1"][1][2] is True
        assert self.data["Sheet1"][2][2] is False
        # Float
        assert self.data["Sheet1"][0][3] == "Float"
        assert self.data["Sheet1"][1][3], 11.11
        # Currency
        assert self.data["Sheet1"][0][4] == "Currency"
        assert self.data["Sheet1"][1][4] == 1
        assert self.data["Sheet1"][2][4] == -10000
        # Percentage
        assert self.data["Sheet1"][0][5] == "Percentage"
        assert self.data["Sheet1"][1][5] == 2
        # int
        assert self.data["Sheet1"][0][6] == "Int"
        assert self.data["Sheet1"][1][6] == 3
        assert self.data["Sheet1"][4][6] == 11
        # Scientifed not supported
        assert self.data["Sheet1"][1][7] == 100000
        # Fraction
        assert self.data["Sheet1"][1][8] == 1.25
        # Text
        assert self.data["Sheet1"][1][9] == "abc"

        @raises(IndexError)
        def test_no_excessive_trailing_columns(self):
            assert self.data["Sheet1"][2][6] == ""
