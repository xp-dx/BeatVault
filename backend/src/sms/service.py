from twilio.rest import Client
from sms.utils import generate_code

# Конфиг Twilio (из переменных окружения)
account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"
twilio_phone = "+1234567890"  # Номер Twilio

client = Client(account_sid, auth_token)


def send_sms_code(phone: str) -> str:
    """Отправляет SMS с кодом подтверждения."""
    code = generate_code(phone)

    # Отправка SMS (режим разработки — вывод в консоль)
    print(f"Код для {phone}: {code}")

    # Реальный запрос к Twilio (раскомментируйте для продакшена)
    # client.messages.create(
    #     body=f"Ваш код подтверждения: {code}",
    #     from_=twilio_phone,
    #     to=phone
    # )
    return code
