cd ..
call venv\Scripts\activate
IF EXIST src\res_compiled (
    rm -rf src\res_compiled\*
) ELSE (
    md src\res_compiled
)
FOR %%I in (res\*.*) DO (
	echo Converting %%I
	call pyrcc5 %%I >> src\res_compiled\%%~nI.py
)
echo Finished