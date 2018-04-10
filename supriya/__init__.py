import pyximport
pyximport.install()
del(pyximport)


import appdirs  # noqa
import pathlib  # noqa
import uqbar.strings  # noqa
output_path = pathlib.Path(appdirs.user_cache_dir('supriya', 'supriya'))
config_path = pathlib.Path(appdirs.user_config_dir('supriya', 'supriya')) / 'supriya.cfg'
if not output_path.exists():
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except IOError:
        pass
if not config_path.exists():
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open('w') as file_pointer:
            file_pointer.write(uqbar.strings.normalize('''
            [core]
                editor = vim
            ''') + '\n')
    except IOError:
        pass
del uqbar
del pathlib
del appdirs


def import_structured_package(
    path,
    namespace,
    remove=True,
    verbose=False,
    ):
    import importlib
    import inspect
    import pathlib
    import traceback
    package_path = pathlib.Path(path).resolve().absolute()
    if not package_path.is_dir():
        package_path = package_path.parent()
    # Determine the package import path
    root_path = package_path
    while (root_path.parent / '__init__.py').exists():
        root_path = root_path.parent
    relative_path = package_path.relative_to(root_path)
    package_import_path = '.'.join((root_path.name,) + relative_path.parts)
    if verbose:
        print(package_import_path)
    # Find importable modules and import their nominative object
    for module_path in sorted(package_path.iterdir()):
        if verbose:
            print('    {}'.format(module_path))
        if module_path.is_dir():
            if verbose:
                print('        Skipping...')
            continue
        else:
            if module_path.suffix not in ('.py', '.pyx'):
                if verbose:
                    print('        Skipping...')
                continue
            module_name = module_path.with_suffix('').name
            if module_name == '__init__':
                if verbose:
                    print('        Skipping...')
                continue
        module_import_path = package_import_path + '.' + module_name
        if verbose:
            print('        Importing {}:{}'.format(module_import_path, module_name))
        module = importlib.import_module(module_import_path)
        try:
            namespace[module_name] = getattr(module, module_name)
        except AttributeError:
            if verbose:
                print('Failed:', module_path)
                traceback.print_exc()
    # Delete this function from the namespace
    this_name = inspect.currentframe().f_code.co_name
    if remove and this_name in namespace:
        del(namespace[this_name])


from supriya import utils  # noqa
from supriya import tools  # noqa
from supriya.tools.miditools import Device  # noqa
from supriya.tools.livetools import Application, Mixer  # noqa
from supriya.tools.nonrealtimetools import Session  # noqa
from supriya.tools.servertools import (  # noqa
    AddAction,
    Buffer,
    BufferGroup,
    Bus,
    BusGroup,
    Group,
    Server,
    Synth,
    )
from supriya.tools.soundfiletools import (  # noqa
    HeaderFormat,
    SampleFormat,
    SoundFile,
    play,
    render,
    )
from supriya.tools.synthdeftools import (  # noqa
    CalculationRate,
    DoneAction,
    Envelope,
    Parameter,
    ParameterRate,
    Range,
    SynthDef,
    SynthDefBuilder,
    SynthDefFactory,
    )
from supriya.tools.systemtools import (  # noqa
    Assets,
    Bindable,
    Binding,
    Enumeration,
    TestCase,
    bind,
    )
from supriya.tools.wrappertools import (  # noqa
    Say,
    )
from abjad.tools.topleveltools import (  # noqa
    graph,
    )
from supriya import synthdefs  # noqa
from supriya.tools import *  # noqa
from supriya.tools import responsetools  # noqa
from supriya._version import __version__, __version_info__  # noqa
