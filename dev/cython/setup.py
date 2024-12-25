from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        Extension(
            "spi_reader",
            sources=["spi_reader.pyx", "spi_backend.c"],  # Include the implementation file
            libraries=["bcm2835"],  # Link bcm2835 library
            include_dirs=["."],  # Ensure the header file is found
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        compiler_directives={"language_level": "3"},
    )
)
