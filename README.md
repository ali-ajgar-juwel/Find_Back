# FindBack — Smart Lost & Found Platform

A Django learning project featuring report CRUD, accounts, owner permissions, search/filter/pagination, image uploads, claim requests, admin, REST API, local-memory caching, a responsive UI, and tests.

## Setup on Windows PowerShell

Open PowerShell in the folder that contains `manage.py` (the `SmartLostFound` folder inside the extracted ZIP):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations reports
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If your terminal already has an active virtual environment, you do not need to create another one.

## Pages
- Website: http://127.0.0.1:8000/
- Browse reports: http://127.0.0.1:8000/reports/
- Developer API guide: http://127.0.0.1:8000/api-guide/
- Browsable API root: http://127.0.0.1:8000/api/
- API reports: http://127.0.0.1:8000/api/reports/
- API categories: http://127.0.0.1:8000/api/categories/
- Admin: http://127.0.0.1:8000/admin/

## API examples
- Search: `/api/reports/?search=wallet`
- Filter by type: `/api/reports/?report_type=LOST`
- Filter by status: `/api/reports/?status=OPEN`
- Filter by category: `/api/reports/?category=1`
- Ordering: `/api/reports/?ordering=-created_at`
- Pagination: `/api/reports/?page=2`

The homepage, report listings, and public report/category API GET responses are cached for 60 seconds using Django's local-memory cache. Successful report/claim changes clear the cache. This cache is suitable for local development; use Redis or Memcached for production or multi-worker deployments.

## First run checklist
1. Open `/admin/` and add categories such as Electronics, Documents, Bags, and Other.
2. Sign up through `/signup/`.
3. Create a Lost or Found report.
4. Use search and filters on `/reports/`.
5. Create another account and submit a claim on another user's open report.
6. Log in as the report owner to approve/reject claims.
7. Run tests with `python manage.py test`.

## Deployment note
This is a local-development project. Before deployment, configure environment variables for the secret key, set `DEBUG=False`, configure allowed hosts, HTTPS/secure cookies, email, media storage, and a production database/cache.
