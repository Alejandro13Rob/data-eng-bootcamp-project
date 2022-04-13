FROM	apache/airflow:2.2.3-python3.7


USER	root
COPY	requirements.txt	./requirements.txt
COPY	start.sh	./start.sh

RUN	    pip install -r requirements.txt && \
        chmod	+x	./start.sh
USER	airflow

EXPOSE	8080

CMD ["/bin/bash",  "start.sh"]