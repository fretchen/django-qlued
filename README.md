[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# django-qlued

A django package the couples together quantum hardware and endusers. It allows cold atom hardware and simulators to be accessed through the `qiskit-cold-atom` and the `sqooler` SDK:

- `qlued` handles the user management and stores the received *json* file in an appropiate queue.
- `qiskit-cold-atom` allows the enduser to write the circuit definitions on its laptop and send them to the server in form of a nice *json* file.
- `sqooler` acts as the SDK that pulls the the calculations from the queue and sends back the result into the storage.
- end devices like the [sqooler-example](https://github.com/Alqor-UG/sqooler-example) or the [labscript-qc-example](https://github.com/Alqor-UG/labscript-qc-example) can perform the calculation and display it to the user.

## Getting started

You can currently install the package via pip through:

```
pip install git+https://github.com/Alqor-UG/django-qlued.git
```

We provide a template for a simple startup:

- The fully deployable example is accessible via [qlued](https://github.com/Alqor-UG/qlued).
- Examples for configurations can be found in the `tests` folder.

## Contributing

See [the contributing guide](docs/contributing.md) for detailed instructions on how to get started with a contribution to our project. We accept different **types of contributions**, most of them don't require you to write a single line of code.

On the [qlued](https://alqor-ug.github.io/django-qlued/) site, you can click the make a contribution button at the top of the page to open a pull request for quick fixes like typos, updates, or link fixes.

For more complex contributions, you can [open an issue](https://github.com/alqor-ug/django-qlued/issues) to describe the changes you'd like to see.

If you're looking for a way to contribute, you can scan through our [existing issues](https://github.com/alqor-ug/django-qlued/issues) for something to work on. 

### Join us in discussions

We use GitHub Discussions to talk about all sorts of topics related to documentation and this site. For example: if you'd like help troubleshooting a PR, have a great new idea, or want to share something amazing you've learned in our docs, join us in the [discussions](https://github.com/alqor-ug/django-qlued/discussions).

## License

Any code within this repo is licenced under the [Apache 2](LICENSE) licence.

The qlued documentation in the docs folders are licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).


## Thanks :purple_heart:

Thanks for all your contributions and efforts towards improving qlued. We thank you for being part of our :sparkles: community :sparkles:!