class FilterModule(object):

    def filters(self):
        return {'to_env': self.to_env}
    
    @staticmethod
    def flatten_dict(d, parent_key='', sep='_'):
        flattened_dict = {}
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                flattened_dict.update(FilterModule.flatten_dict(v, new_key, sep=sep))
            else:
                flattened_dict[new_key] = v
        return(flattened_dict)

    def to_env(self, variable):
        d = FilterModule.flatten_dict(variable)
        env_string = ""
        for k,v in d.items():
            if v is None:
                v = ""
            env_string += "{}={}\n".format(k.upper(), v)
        return(env_string)
