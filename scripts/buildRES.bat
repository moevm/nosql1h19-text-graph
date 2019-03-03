cd ..
call venv\Scripts\activate
IF EXIST src\res (
    rm -rf src\res\*
) ELSE (
    md src\res
)
FOR %%I in (res\*.*) DO (
	echo Converting %%I
	call pyrcc5 %%I >> src\res\%%~nI.py
)
echo Finished