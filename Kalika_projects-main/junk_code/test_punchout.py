from flask import Flask, request, Response
import xml.etree.ElementTree as ET

app = Flask(__name__)


@app.route('/punchout', methods=['POST'])
def punchout():
    # Process the incoming PunchOutSetupRequest
    # Here you would typically validate the request

    # Create the PunchOutSetupResponse
    response_xml = ET.Element('cXML')
    response = ET.SubElement(response_xml, 'PunchOutSetupResponse')
    start_page = ET.SubElement(response, 'StartPage')
    start_page.text = 'https://lemonchiffon-ram-961910.hostingersite.com'

    return Response(ET.tostring(response_xml), mimetype='text/xml')


if __name__ == '__main__':
    app.run(debug=True)