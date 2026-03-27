FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy source
COPY src/words_maker/ ${LAMBDA_TASK_ROOT}/words_maker/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

CMD ["lambda_handler.handler"]
