update-requirements.txt: requirements.txt
	poetry export --output "stable_diffusion/requirements.txt" --with="stable-diffusion"
	poetry export --output "api/requirements.txt" --with="api"
	poetry export --output "requirements.txt" --with="stable-diffusion,api"
