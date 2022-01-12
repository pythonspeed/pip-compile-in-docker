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

You will now have a `requirements.txt` file that looks a little like this:

```
# ...
click==8.0.3 \
    --hash=sha256:353f466495adaeb40b6b5f592f9f91cb22372351c84caeb068132442a4518ef3 \
    --hash=sha256:410e932b050f5eed773c4cda94de75971c89cdb3155a72a0831139a79e5ecb5b
    # via flask
flask==2.0.2 \
    --hash=sha256:7b2fb8e934ddd50731893bdcdb00fc8c0315916f9fcd50d22c7cc1a95ab634e2 \
    --hash=sha256:cb90f62f1d8e4dc4621f52106613488b5ba826b2e1e10a33eac92f723093ab6a
    # via -r /input/requirements.in
# ...
```

(Choose the matching Docker image for whatever Python version you actually use in production.)

Check-in both `requirements.in` and `requirements.txt` into version control, install your application dependencies using the latter, and update your dependencies by re-running this command.

To learn more about what the tool is doing, see the [underlying `pip-tools` documentation](https://github.com/jazzband/pip-tools/).

> <a href="https://pythonspeed.com/products/productionhandbook/"><img src="https://pythonspeed.com/products/productionhandbook/cover.png" align="right" width="20%"></a> This tool is sponsored by the [Python on Docker Production Handbook](https://pythonspeed.com/products/productionhandbook/), your complete reference for packaging Python applications for Docker in production.
> <br clear="right">

## Motivation

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
