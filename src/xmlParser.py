# src/xmlParser.py
import xml.dom.minidom
import re

class xmlParser:
    @staticmethod
    def xmlParserBeautify(xml_string):
        try:
            # Menghapus whitespace di awal dan akhir
            xml_string = xml_string.strip()
            
            # Mengganti karakter escape '\n' dengan newline sebenarnya
            xml_string = xml_string.replace('\\n', '\n')
            
            # Menghapus newline dan whitespace berlebih di antara tag
            xml_string = re.sub(r'\s*\n\s*', '', xml_string)
            
            # Parsing string XML
            dom = xml.dom.minidom.parseString(xml_string)
            
            # Pretty-print XML dengan indentasi tab
            pretty_xml = dom.toprettyxml(indent="\t")
            
            # Menghapus baris kosong
            pretty_xml = re.sub(r'\n\s*\n', '\n', pretty_xml)
            
            # Menghapus baris pertama (deklarasi XML) jika ada
            pretty_xml = re.sub(r'<\?xml.*\?>\n', '', pretty_xml)
            
            return pretty_xml.strip()
        except Exception as e:
            return f"Error parsing XML: {str(e)}"

    @staticmethod
    def xmlParserMinify(xml_string):
        try:
            # Menghapus whitespace di awal dan akhir
            xml_string = xml_string.strip()
            
            # Mengganti karakter escape '\n' dengan newline sebenarnya
            xml_string = xml_string.replace('\\n', '\n')
            
            # Menghapus newline dan whitespace berlebih di antara tag
            minified_xml = re.sub(r'\s*\n\s*', '', xml_string)
            minified_xml = re.sub(r'\s+', ' ', minified_xml)
            minified_xml = re.sub(r'>\s+<', '><', minified_xml)
            
            return minified_xml.strip()
        except Exception as e:
            return f"Error minifying XML: {str(e)}"