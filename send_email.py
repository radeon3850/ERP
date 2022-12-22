import smtplib

smtpObj = smtplib.SMTP('smtp.ukr.net', 465 )

smtpObj.starttls()