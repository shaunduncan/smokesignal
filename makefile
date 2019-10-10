# build/dist step automation for membrane

S3PYPI_BUCKET			=	pypi1.bright.md
S3PYPI_SECRET			=	$(shell aws secretsmanager --query SecretString get-secret-value --secret-id /dev/pypi1.bright.md/url-secret | jq -r 'fromjson | .secret')
ifeq ($(strip $(S3PYPI_SECRET)),)
$(error S3PYPI_SECRET unset)
endif
VIRTUALENV_PYTHON2		=	$(WORKON_HOME)/smokesignal
VIRTUALENV_PYTHON3		=	$(WORKON_HOME)/smokesignal3

MEMBRANE_VERSION		= 	$(shell python setup.py --version)

SOURCE_PACKAGE			=	dist/smokesignal-$(MEMBRANE_VERSION).tar.gz
BINARY_PACKAGE_PYTHON2	=	dist/smokesignal-$(MEMBRANE_VERSION)-py2-none-any.whl
BINARY_PACKAGE_PYTHON3	=	dist/smokesignal-$(MEMBRANE_VERSION)-py3-none-any.whl

.PHONY: s3pypi

all:

$(SOURCE_PACKAGE):
	python setup.py sdist

$(BINARY_PACKAGE_PYTHON2):
	. $(VIRTUALENV_PYTHON2)/bin/activate && python setup.py bdist_wheel

$(BINARY_PACKAGE_PYTHON3):
	. $(VIRTUALENV_PYTHON3)/bin/activate && python setup.py bdist_wheel

s3pypi: $(SOURCE_PACKAGE) $(BINARY_PACKAGE_PYTHON2) $(BINARY_PACKAGE_PYTHON3)
	echo . $(VIRTUALENV_PYTHON2)/bin/activate && echo s3pypi --secret $(S3PYPI_SECRET)/python2 --bucket $(S3PYPI_BUCKET)
	echo . $(VIRTUALENV_PYTHON3)/bin/activate && echo s3pypi --secret $(S3PYPI_SECRET)/python3 --bucket $(S3PYPI_BUCKET)
