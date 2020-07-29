# How to Contribute to the Grammar Matrix

# Local Testing

These are some (historical) notes for testing the questionnaire locally.
Mileage may vary.

> To test the customization facilities without uploading to homer:
>
> 1. Create a subdirectory under sessions/ called '000' ('001', etc).
> 
> 2. Set the following shell variables:
>
>        export REQUEST_METHOD=GET
>        export QUERY_STRING="customize=x&delivery=tgz"
>        export HTTP_COOKIE=session=000
>
> 3. Put an appropriate choices file in 000/
>
> 4. `python matrix.cgi`

