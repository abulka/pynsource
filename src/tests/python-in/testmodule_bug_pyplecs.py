import time
import shutil
import os
import pywinauto

from pathlib import Path

import xmlrpc.client

import psutil
import subprocess
import re
import copy

import scipy.io as sio

command = r"C:/Program Files/Plexim/PLECS 4.2 (64 bit)/plecs.exe"
command = r"C:/Program Files/Plexim/PLECS 4.3 (64 bit)/plecs.exe"
# command = r"C:\Users\tinix\Documents\Plexim\PLECS 4.3 (64 bit)\PLECS.exe"

def load_mat_file(file):
    param = sio.loadmat(file)
    del param['__header__']
    del param['__version__']
    del param['__globals__']
    return param

def save_mat_file(file_name, data):
    sio.savemat(file_name, data, format='5')


def dict_to_plecs_opts(varin: dict):
    for k, _ in varin.items():
        varin[k] = float(varin[k])
    opts = {'ModelVars': varin}
    return opts


def generate_variant_plecs_file(scr_filename: str, dst_filename: str, modelvars: dict):
    # keyword grammar for parser
    start_init_cmd = 'InitializationCommands'
    end_init_cmd = 'InitialState'

    dst_path_obj = Path(dst_filename)

    try:
        os.mkdir(dst_path_obj.parent)
    except FileExistsError:
        shutil.rmtree(dst_path_obj.parent)
        os.mkdir(dst_path_obj.parent)

    fp_src = open(str(scr_filename), "r")
    fp_dst = open(str(dst_filename), "w+")

    state = 'copy'
    for _, line in enumerate(fp_src):
        if start_init_cmd in line:
            state = 'edit'
        if end_init_cmd in line:
            state = 'copy'

        if state == 'edit':
            for var_name, value in modelvars.items():
                regex = var_name + r"([\s\=\d\.]+)\;"
                try:
                    old_var_str = (re.search(regex, line)).group(0)
                    new_var_str = f"{var_name} = {value};"
                    line = line.replace(old_var_str, new_var_str)
                except AttributeError:
                    pass
        fp_dst.writelines(line)

    fp_src.close()
    fp_dst.close()


def generate_variant_plecs_mdl(src_mdl, variant_name: str, variant_vars: dict):
    variant_mdl = copy.deepcopy(src_mdl)
    src_path_obj = Path(src_mdl.filename)
    variant_mdl.filename = str(src_path_obj.parent / variant_name / src_path_obj.name).replace('.plecs',
                                                                                               f'{variant_name}.plecs')
    generate_variant_plecs_file(scr_filename=src_mdl.filename, dst_filename=variant_mdl.filename,
                                modelvars=variant_vars)

    return variant_mdl


class PlecsApp:
    def __init__(self):
        self.command = command
        self.app = pywinauto.application.Application(backend='uia')
        self.app.start(self.command)
        self.app_gui = self.app.connect(path=self.command)

    #    @staticmethod
    def set_plecs_high_priority(self):
        proc_iter = psutil.process_iter(attrs=["pid", "name"])
        for p in proc_iter:
            if p.info["name"] == "PLECS.exe":
                # print (p.pid)
                proc = psutil.Process(p.pid)
                proc.nice(psutil.HIGH_PRIORITY_CLASS)

    #    @staticmethod
    def open_plecs(self):
        try:
            pid = subprocess.Popen([command], creationflags=psutil.ABOVE_NORMAL_PRIORITY_CLASS).pid
        except Exception:
            print('Plecs opening problem')
	#return pid

    #    @staticmethod
    def kill_plecs(self):
        proc_iter = psutil.process_iter(attrs=["pid", "name"])
        for p in proc_iter:
            if p.info["name"] == "PLECS.exe":
                # print (p.pid)
                p.kill()

    #    @staticmethod
    def get_plecs_cpu(self):
        proc_iter = psutil.process_iter(attrs=["pid", "name"])
        value = 0
        cpu_usage = None
        for p in proc_iter:
            if p.info["name"] == "PLECS.exe":
                cpu_usage = max(value, p.cpu_percent())
        return cpu_usage

    def run_simulation_by_gui(self, plecs_mdl):
        mdl_app = self.app.connect(title=str(plecs_mdl._model_name), class_name='Qt5QWindowIcon')
        mdl_app[str(plecs_mdl._name)].set_focus()
        mdl_app[str(plecs_mdl._name)].menu_select('Simulation')
        pywinauto.keyboard.send_keys('{DOWN}')
        pywinauto.keyboard.send_keys('{ENTER}')
        # TBTested
        # pywinauto.keyboard.send_keys('^t')

    def load_file(self, plecs_mdl, mode='XML-RPC'):
        if mode=="gui":
            pwa_app = pywinauto.application.Application()
            qtqwindowicon = pwa_app.connect(title=u'Library Browser', class_name='Qt5QWindowIcon').Qt5QWindowIcon
            qtqwindowicon.set_focus()
            pywinauto.keyboard.send_keys('^o')
            #TODO: filling window open file
        elif mode=="XML-RPC":
            PlecsServer(plecs_mdl.folder, plecs_mdl.simulation_name, load=True)
        else:
            raise  Exception("Not implemented mode")
        
        return None

    def check_if_simulation_running(self, plecs_mdl):
        # TODO: check title of the simulation and return if contain running
        pass


class PlecsServer:
    def __init__(self, sim_path=None, sim_name=None, port='1080', load=True):
        self.modelName = sim_name.replace('.plecs', '')
        self.server = xmlrpc.client.Server('http://localhost:' + port + '/RPC2')
        self.sim_name = sim_name
        self.sim_path = sim_path
        self.optStruct = None

        if ((sim_path is not None) or ( sim_name is not None)) and load:
            self.server.plecs.load(self.sim_path + '//' + self.sim_name)
        else:
            print('sim_path or sim_path is invalid or load is False')
            print(f'load={load}')

    def run_sim_single(self, inputs):
        inputs = load_mat_file(inputs)
        for name, value in inputs.items():
            self.load_model_var(name, value)
        results = self.server.plecs.simulate(self.modelName, self.optStruct)
        return results

    def load_file(self):
        self.load()

    def load(self):
        """ 
        Interface to the plecs.load function 
        from Plecs help: plecs.load('mdlFileName')
        """
        self.server.plecs.load(self.sim_path + '//' + self.sim_name)

    def close(self):
        """  
        Interface to the plecs.close function 
        from Plecs help: plecs.close('mdlName')
        """
        self.server.plecs.close(self.modelName)

    def load_model_vars(self, data):
        varin = {**self.optStruct['ModelVars'], **data}
        for k, _ in varin.items():
            varin[k] = float(varin[k])  # float conversion due to XML protocol limitation
        opts = {'ModelVars': varin}
        return opts

    def load_model_var(self, name, value):
        if not hasattr(self, 'opts'):
            self.optStruct = {'ModelVars': dict()}
        self.optStruct['ModelVars'][name] = float(value)

    def load_modelvars(self, model_vars: dict):
        #TODO: merge with load_model_vars
        if 'ModelVars' in model_vars:
            # self.optStruct = {'ModelVars': dict()}
            self.optStruct = model_vars
        else:
            self.optStruct = dict_to_plecs_opts(varin=model_vars)

    def set_value(self, ref, parameter, value):
        self.server.plecs.set(self.modelName + '/' + ref, parameter, str(value))

    def run_sim_with_datastream(self, param_dict=None):
        """
        Kick off PLECS simulation with specified
        @param param_dict parameter dictionary for the PLECS circuit
        @return simulation data in case ouput is present in the model
        """
        if param_dict is None:
            return self.server.plecs.simulate(self.modelName)
        else:
            self.load_modelvars(model_vars=param_dict)
            return self.server.plecs.simulate(self.modelName, self.optStruct)


class GenericConverterPlecsMdl:
    def __init__(self, filename: str):
        # simulation file
        path_obj = Path(filename)
        self._type = path_obj.suffix[1:]
        self._folder = path_obj.parent
        self._name = path_obj.name  # PLECS Model name with filetype extension
        self._model_name = self._name.replace('.plecs', '')
        self._fullname = path_obj
        # simulation vars
        self.optStruct = self.set_default_model_vars()
        # I/O section
        self.components_vars = {}
        self.outputs_vars = {}
        # server section
        # self.server = PlecsServer(sim_path=str(self._folder), sim_name=self._name)

    def __repr__(self, *args, **kwargs):  # real signature unknown
        """ Return repr(self). """
        pass

    # def load_modelvars_struct_from_plecs(self):
    #     # TODO: read input parameter list from plecs file, parsing init workspace
    #     pass

    # def load_input_vars(self):
    #     # TODO: read from workspace write to plecs file
    #     pass

    def set_default_model_vars(self):
        varin = dict()
        varin['Vi'] = 0.0
        varin['Vo'] = 0.0
        # convert each item to float (XLM-RPC doesnt support numpy type)
        for k, _ in varin.items():
            varin[k] = float(varin[k])
        opts = {'ModelVars': varin}
        return opts

    @property
    def filename(self):
        ''' PLECS Model name with filetype extension and full address '''
        return str(self._fullname)

    @property
    def folder(self):
        ''' PLECS Model folder full address '''
        return str(self._folder)

    @property
    def model_name(self):
        ''' PLECS Model name without filetype extension '''
        return str(self._model_name)

    @property
    def simulation_name(self):
        ''' PLECS Model name with filetype extension '''
        return str(self._name)

    @filename.setter
    def filename(self, filename: str):
        path_obj = Path(filename)
        self._type = path_obj.suffix
        self._folder = path_obj.parent
        self._name = path_obj.name
        self._fullname = path_obj
        self._model_name = self._name.replace('.plecs', '')


# if __name__ == "__main__":
#    plecs42 = PlecsApp()
#    plecs42.kill_plecs()
#    time.sleep(1)
#    plecs42.open_plecs()
#    time.sleep(1)
#    plecs42.set_plecs_high_priority()
#
#    sim_path = "./"
#    sim_name = "simple_buck.plecs"
