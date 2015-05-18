import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import subprocess


ext = Extension('nllsCuda',
                sources=['cppIntegration.cu', 'interface.pyx'],
                library_dirs=['/usr/local/cuda-6.0/lib64'],
                libraries=['cudart'],
                language='c++',
                runtime_library_dirs=['/usr/local/cuda-6.0/lib64'],
                # this syntax is specific to this build system
                # we're only going to use certain compiler args with nvcc and not with gcc
                # the implementation of this trick is in customize_compiler() below
                extra_compile_args={'gcc': [],
                                    'nvcc': ['-arch=compute_20', '-code=sm_21,sm_35', '--ptxas-options=-v', '-c', '--compiler-options', "'-fPIC'"]},
                include_dirs = ['/usr/local/cuda-6.0/include'])



def customize_compiler_for_nvcc(self):
    """inject deep into distutils to customize how the dispatch
to gcc/nvcc works.
If you subclass UnixCCompiler, it's not trivial to get your subclass
injected in, and still have the right customizations (i.e.
distutils.sysconfig.customize_compiler) run on it. So instead of going
the OO route, I have this. Note, it's kindof like a wierd functional
subclassing going on."""
    
    # tell the compiler it can processes .cu
    self.src_extensions.append('.cu')

    # save references to the default compiler_so and _comple methods
    default_compiler_so = self.compiler_so
    super = self._compile

    # now redefine the _compile method. This gets executed for each
    # object but distutils doesn't have the ability to change compilers
    # based on source extension: we add it.
    def _compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
        if os.path.splitext(src)[1] == '.cu':
            # use the cuda for .cu files
            self.set_executable('compiler_so', '/usr/bin/nvcc')
            # use only a subset of the extra_postargs, which are 1-1 translated
            # from the extra_compile_args in the Extension class
            postargs = extra_postargs['nvcc']
        else:
            postargs = extra_postargs['gcc']

        super(obj, src, ext, cc_args, postargs, pp_opts)
        # reset the default compiler_so, which we might have changed for cuda
        self.compiler_so = default_compiler_so

    # inject our redefined _compile method into the class
    self._compile = _compile


# run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        customize_compiler_for_nvcc(self.compiler)
        build_ext.build_extensions(self)

setup(name='pdoa_nlls',
      # random metadata. there's more you can supploy
      author='Sondre Engebraaten',
      version='1.0',

      ext_modules = [ext],

      # inject our custom trigger
      cmdclass={'build_ext': custom_build_ext},

      # since the package has c code, the egg cannot be zipped
      zip_safe=False)
