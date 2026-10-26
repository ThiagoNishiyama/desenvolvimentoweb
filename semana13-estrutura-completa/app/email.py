import json
import subprocess
from flask import current_app, render_template


def send_email(to, subject, template, **kwargs):
    api_key = current_app.config.get('API_KEY')
    if not api_key:
        current_app.logger.warning('API_KEY nao configurado')
        return False
    html_body = render_template(template + '.html', **kwargs)
    recipients = to if isinstance(to, list) else [to]
    payload = json.dumps({
        'personalizations': [{'to': [{'email': r} for r in recipients]}],
        'from': {'email': current_app.config['API_FROM'], 'name': 'Flasky'},
        'subject': current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        'content': [{'type': 'text/html', 'value': html_body}],
    })
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', current_app.config['API_URL'],
             '-H', 'Authorization: Bearer ' + api_key,
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=15
        )
        current_app.logger.info(f'SendGrid status={result.returncode}')
        return True
    except Exception as e:
        current_app.logger.error(f'Erro email: {e}')
        return False
