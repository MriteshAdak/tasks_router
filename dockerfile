FROM public.ecr.aws/lambda/python:3.12.2026.06.02.15-x86_64

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY . .

CMD ["lambda_function.handler"]