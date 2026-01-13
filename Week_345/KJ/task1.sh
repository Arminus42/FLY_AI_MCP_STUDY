#!/bin/bash

# 1부터 6까지 반복 (i가 1, 2, ..., 6으로 변함)
for i in {1..6}
do
    echo "============================================"
    echo "Running Task for example$i.py..."
    echo "============================================"

    # $i 변수를 문자열 사이에 넣어서 명령어를 동적으로 완성합니다.
    python mcp-client-task-1.py tools-task-1.py "List the files in /targets, read example$i.py, and generate a test file for example$i.py."
    
    # (선택 사항) 서버 부하 방지를 위해 1초 대기
    sleep 1
    echo "" 
done