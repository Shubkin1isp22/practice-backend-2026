# Шубкин С.М. | 1ИСП-21 | Сервис опросов
## 1. Стек:
 - Flask
 - PostgreSQL

## 2. Изображение er-диаграммы бд проекта
!["Диаграмма"](./docs/er-diagram.png)

## 3. Список эндпоинтов:
### Auth
	•	POST /auth/register
	•	POST /auth/login
	•	GET /auth/me
### Surveys
	•	POST /surveys
	•	GET /surveys
	•	GET /surveys/{id}
	•	PUT /surveys/{id}
	•	POST /surveys/{id}/publish
	•	POST /surveys/{id}/close
### Questions
	•	POST /surveys/{id}/questions
	•	PUT /questions/{id}
	•	DELETE /questions/{id}
### Options
	•	POST /questions/{id}/options
	•	PUT /options/{id}
	•	DELETE /options/{id}
### Analytics
	•	GET /surveys/{id}/results
## 4. Миграции: