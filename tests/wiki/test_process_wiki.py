import os
import filecmp
import unittest
from ccquery.preprocessing import WikiExtraction
from ccquery.utils import io_utils

def count_lines(file):
    """Return the number of lines within a file"""
    n = 0
    with open(file, 'r') as istream:
        for line in istream:
            n += 1
    return n

def delete_temp_file(file):
    """Delete temporary files"""
    if os.path.exists(file):
        os.remove(file)

class TestWikiProcessing(unittest.TestCase):
    """Test the wiki extraction methods"""

    def setUp(self):
        """Set up local variables"""

        self.extractor = WikiExtraction()
        self.sample = os.path.join(os.path.dirname(__file__), 'sample.bz2')
        self.data = os.path.join(os.path.dirname(__file__), 'sample-corpus.txt')
        self.vocab = os.path.join(os.path.dirname(__file__), 'sample-vocab.txt')

        io_utils.check_file_readable(self.sample)
        io_utils.check_file_readable(self.data)
        io_utils.check_file_readable(self.vocab)

        # temporary files
        self.files = {
            'xml':   io_utils.change_extension(self.sample, 'xml'),
            'jsonl': io_utils.change_extension(self.sample, 'jsonl'),
            'txt':   io_utils.change_extension(self.sample, 'txt'),
            'voc':   io_utils.change_extension(self.sample, 'voc.txt'),
        }

    def tearDown(self):
        """Remove temporary files"""
        for file in self.files.values():
            delete_temp_file(file)

    def test_sequential_processing(self):
        """Test the all the intermediate wikidump processings"""
        self.execute_decompress(self.sample, self.files['xml'])
        self.execute_extract(self.files['xml'], self.files['jsonl'])
        self.execute_sentences(self.files['jsonl'], self.files['txt'])
        self.execute_vocabulary(self.files['txt'], self.files['voc'])

    def execute_decompress(self, fin, fout):
        """Test the decompress feature"""
        self.extractor.save_xml(fin, fout)
        self.assertEqual(os.path.exists(fout), True)
        self.assertEqual(count_lines(fout), 366)

    def execute_extract(self, fin, fout):
        """Test the wiki extraction feature"""
        args = [
            '--quiet',
            '--json',
            '--bytes 30G',
            '--processes 2',
            '--no-templates',
            '--filter_disambig_pages',
            '--min_text_length 50',
        ]
        self.extractor.save_content(fin, fout, args)
        self.assertEqual(os.path.exists(fout), True)
        self.assertEqual(count_lines(fout), 3)

    def execute_sentences(self, fin, fout):
        """Test the sentence division feature"""
        kwargs = {
            'ignore_digits': True,
            'apostrophe': 'fr',
            'ignore_punctuation': 'noise-a',
            'tostrip': False,
            'keepalnum': True,
        }
        self.extractor.save_sentences(fin, fout, 'text', **kwargs)
        self.assertEqual(os.path.exists(fout), True)
        self.assertEqual(count_lines(fout), 111)
        self.assertTrue(
            filecmp.cmp(self.data, fout, shallow=False),
            'Generated corpus different from reference corpus')

    def execute_vocabulary(self, fin, fout):
        """Test the vocabulary definition feature"""
        kwargs = {'topn': 500}
        self.extractor.load_words(fin)
        self.extractor.filter_words(**kwargs)
        self.extractor.save_words(fout)
        self.assertEqual(os.path.exists(fout), True)
        self.assertEqual(count_lines(fout), 500)
        self.assertTrue(
            filecmp.cmp(self.vocab, fout, shallow=False),
            'Generated vocabulary different from reference vocabulary')