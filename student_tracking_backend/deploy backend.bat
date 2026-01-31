@echo off
echo Building new image...
call gcloud builds submit --tag gcr.io/canvas-voltage-485413-t9/student-backend

echo Deploying to Cloud Run...
call gcloud run deploy student-api --image gcr.io/canvas-voltage-485413-t9/student-backend --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances="canvas-voltage-485413-t9:us-central1:student-tracking-project" --set-env-vars="DB_USER=postgres,DB_PASS=NnoK@133994,DB_NAME=student_tracking,INSTANCE_CONNECTION_NAME=canvas-voltage-485413-t9:us-central1:student-tracking-project,MAIL_USERNAME=schooltrackingproject@gmail.com,MAIL_PASSWORD=bzco ygio kgov ekzh,MAIL_SERVER=smtp.gmail.com,MAIL_PORT=587"

echo Done!
pause