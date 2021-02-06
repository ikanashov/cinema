FROM python:3-alpine as base
                                                                                                          
FROM base as builder

RUN mkdir /install
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev linux-headers
WORKDIR /install
COPY requirements /requirements                                                                                       
RUN pip install --upgrade pip && pip install --prefix=/install -r /requirements/dev.txt                                                     
                                                                                                                              
FROM base                                                                                                                     
                                                                                                                              
COPY --from=builder /install /usr/local                                                                                       
COPY . /cinema_admin
RUN apk --no-cache add libpq                                                                                                  
WORKDIR /cinema_admin