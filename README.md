> This tool is sponsored by the [Python on Docker Production Handbook](https://pythonspeed.com/products/productionhandbook/), your complete reference to packaging Python applications for Docker in production.

# Pin your Python dependencies!

`pin-requirements.py` is a script that lets you pin your Python dependencies inside a Docker container.

* Pinning your dependencies is great because it gives you reproducible builds.
  [See below for more motivations](#motivation).
* `pip` installs different dependencies depending on the version of Python, and which operating system you're using.
  So if you're deploying on Linux, doing the pinning inside Docker means you get consistent, correct pinning.

`pin-requirements.py` is a script based on `pip-tools` that takes the
high-level requirements from `requirements.in` and transitively pins them to
output file `requirements.txt`:

Just create a `requirements.in` listing your top-level dependencies:

```
flask>1.0
```

And then run:

```shell
$ pin-requirements.py --image python:3.9-slim
```

Choose the matching Docker image for whatever Python version you actually use in production.

To learn more about what the tool is doing, see the [underlying `pip-tools` documentation](https://github.com/jazzband/pip-tools/).

## Motivation: why you want to do this {#motivation}

> Note that everything I'm discussing here is focused on applications; libraries are a whole different story.

Every application really requires two different sets of dependency
descriptions:

1. The logical, direct dependencies. For example, "this needs at
   least Flask 1.0 to run".
2. The complete set of dependencies, including transitive dependencies, pinned
   to particular versions. Transitive means dependencies-of-dependencies, and
   pinning means particular versions. For example, this might be "Flask==1.0.3,
   itsdangerous==1.1.0, werkzeug==0.15.4, click==7.0, jinja2==2.10.1,
   markupsafe==1.1.1".

The first set of dependencies can be used to easily update the second set of
dependencies when you want to upgrade (e.g. to get security updates).

The second set of dependencies is what you should use to build the application,
in order to get reproducible builds: that is, to ensure each build will have the
exact same dependencies installed as the previous build.

### Implementing pinned dependencies in `requirements.txt`

Some alternatives include `pipenv` and `poetry`.

Within the framework of existing packaging tools, however, [`pip-tools`](https://github.com/jazzband/pip-tools/) is the
easiest way to take your logical requirement, and turn them into pinned
requirements. You write a `requirements.in` file (in `requirements.txt` format)
listing your direct dependencies in a flexible way:

```requirements
flask>=1.0
```

And then you use `pip-tools` to convert that to a pinned `requirements.txt` you
can use in your project. `setup.py`/`setup.cfg` end up not including any
dependencies at all (note that this setup is specific to applications; libraries
are a different story).
