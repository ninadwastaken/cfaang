import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError

from scripts.check_setup import check_setup


class CheckSetupTests(unittest.TestCase):
    def run_check(self, responses):
        output = io.StringIO()
        with patch('scripts.check_setup.fetch_json', side_effect=responses), \
                redirect_stdout(output):
            result = check_setup('http://localhost:8000')
        return result, output.getvalue()

    def test_healthy_setup(self):
        code, output = self.run_check([
            {'status': 'ok'}, {'status': 'ok'},
            {'Spots': [{'name': 'Cafe'}], 'count': 1}])
        self.assertEqual(code, 0)
        self.assertIn('PASS: Sample meeting search', output)

    def test_unreachable_api(self):
        code, output = self.run_check([URLError('refused')])
        self.assertEqual(code, 1)
        self.assertIn('./local.sh', output)

    def test_database_unavailable(self):
        code, output = self.run_check([
            {'status': 'ok'}, URLError('503')])
        self.assertEqual(code, 1)
        self.assertIn('docker compose up -d mongo', output)

    def test_empty_import(self):
        code, output = self.run_check([
            {'status': 'ok'}, {'status': 'ok'}, {'Spots': [], 'count': 0}])
        self.assertEqual(code, 1)
        self.assertIn('make local_db', output)

    def test_invalid_response(self):
        code, output = self.run_check([{'unexpected': True}])
        self.assertEqual(code, 1)
        self.assertIn('FAIL: API health', output)

    def test_search_failure(self):
        code, output = self.run_check([
            {'status': 'ok'}, {'status': 'ok'}, ValueError('Invalid JSON')])
        self.assertEqual(code, 1)
        self.assertIn('FAIL: Sample meeting search', output)


if __name__ == '__main__':
    unittest.main()
