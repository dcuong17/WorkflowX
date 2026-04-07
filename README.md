# WorkflowX

## Deployment Notes

### Frontend on Vercel
- Deploy the `frontend/` directory as the Vercel project root.
- Set `VITE_API_BASE_URL` to your public backend URL plus `/api/v1`.
- `frontend/vercel.json` already rewrites all SPA routes to `index.html`.

### Backend on AWS Elastic Beanstalk
- Deploy the repo root as the backend project.
- `Procfile` runs Django with `gunicorn`.
- Set the environment variables from `.env.example`.
- Use `DATABASE_URL=mysql://<user>:<password>@<rds-endpoint>:3306/<db_name>` for Amazon RDS MySQL.
- After the frontend domain is known, add it to `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and `ALLOWED_HOSTS`.

### File Uploads
- For AWS production, set `USE_S3=True` and provide the S3 variables from `.env.example`.
- If `USE_S3=False`, uploads fall back to local `MEDIA_ROOT`, which is not recommended for Elastic Beanstalk production.
