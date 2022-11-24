update-requirements.txt: requirements.txt
	poetry export --output "stable_diffusion/requirements.txt" --with="stable-diffusion" --without-hashes
	poetry export --output "api/requirements.txt" --with="api" --without-hashes
	poetry export --output "requirements.txt" --with="api,stable-diffusion,dev,deploy" --without-hashes
