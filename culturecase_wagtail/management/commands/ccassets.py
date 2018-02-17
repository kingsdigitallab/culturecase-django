'''
Created on 15 Feb 2018

@author: jeff
'''

from kdl_wordpress2wagtail.management.commands._kdlcommand import KDLCommand
import re
import os


class Command(KDLCommand):
    help = 'Asset management'

    def add_arguments(self, parser):
        parser.add_argument('action', nargs=1, type=str)
        parser.add_argument('aargs', nargs='*', type=str)

    def action_download(self):
        try:
            root_url = self.aargs.pop(0)
        except Exception:
            return self.print_error('missing argument: URL')
        try:
            self.dir_out = self.aargs.pop(0)
        except Exception:
            return self.print_error('missing argument: output path')

        html = self._fetch_url(root_url)

        html = re.sub(
            r'''(\b(?:href|src)\s*=\s*)['"]([^"']+)["']''',
            self._sub_href,
            html
        )

        # from django.conf import settings
        # import os
        # dir_out = os.path.join(settings.STATIC_ROOT, 'kdlassets')

        self._write_path_and_file('index.html', html, self.dir_out)

        print('Files saved under {}'.format(self.dir_out))

    def _fetch_url(self, url):
        ret = None

        # read or download the page
        file_prefix = 'file://'
        if url.startswith(file_prefix):
            ret = self._read_file(url.replace(file_prefix, '/'))
        else:
            import requests
            res = requests.get(url)
            ret = res.content

        return ret

    def _read_file(self, filepath, encoding='utf-8'):
        import codecs
        f = codecs.open(filepath, 'r', encoding)
        ret = f.read()
        f.close()

        return ret

    def _write_path_and_file(self, file_path, content, path, encoding='utf8'):
        file_path = os.path.join(path, file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self._write_file(file_path, content, encoding)

    def _write_file(self, file_path, content, encoding='utf8'):
        f = open(file_path, 'wb')
        if encoding:
            content = content.encode(encoding)
        f.write(content)
        f.close()

    def _sub_href(self, match):
        ret = match.group(0)

        url = match.group(2)
        from urllib import parse
        parts = parse.urlparse(url)

        print(url)

        if parts.scheme not in 'mailto':
            category = self._get_content_category_from_path(parts.path)
            # print(repr(category))

            if category:
                query = parts.query
                if query:
                    query = '?' + query
                file_path = ''.join([parts.netloc, parts.path])
                # we drop the query string as {% static doesn't support them
                new_path = "\"{% static '" + file_path + "' %}\""
                ret = match.group(1) + new_path

                print('  ' + ret)

                if 0:
                    content = self._fetch_url(url)
                    self._write_path_and_file(
                        file_path, content, self.dir_out, encoding=None)

        return ret

    def _get_content_category_from_path(self, path):
        ret = None

        ext = re.sub(r'^(.*?\.)([^./]+)$', r'\2', path)
        if ext and ext != path:
            ret = ext

        return ret

    def show_help(self):
        ret = '''
actions:

  download URL
    download all the assets referenced by URL into the assets folder
        '''

        self.stdout.write(ret)

        return ret
