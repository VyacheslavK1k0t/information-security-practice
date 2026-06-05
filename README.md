# Electronic Dean's Office

## Опис
REST API на базі FastAPI + SQLite. Практична робота з дисципліни "Безпека інформаційних систем".

## Запуск
```bash
git clone <url-репозиторію>
cd information-security-practice
docker compose up --build

## API Authentication
Система підтримує реєстрацію та авторизацію користувачів з безпечним хешуванням паролів (bcrypt).

### Ендпоінти
- `POST /auth/register`: Реєстрація нового користувача. Приймає JSON з полями `username`, `email`, `password`.
- `POST /auth/login`: Авторизація користувача. Перевіряє хешований пароль у базі даних.

### Тестові облікові записи
Для перевірки роботи API ви можете використовувати наступні логіни:
- `admin`
- `newstudent`

*Примітка: Паролі до цих акаунтів не публікуються з міркувань безпеки.*