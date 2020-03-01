from ..Script import Script
class ModifyByHeight(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"ModifyByHeight",
            "key": "ModifyByHeight",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "height_start":
                {
                    "label": "Switch height start",
                    "description": "At what height switch should start",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.0
                },
                "height_inc":
                {
                    "label": "Switch increment height",
                    "description": "At what height should the pause occur",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5.0
                },
                "acc_enable":
                {
                    "label": "Acceleration enable",
                    "description": "Enable acceleration change",
                    "type": "bool",
                    "default_value": false
                },
                "acc_start":
                {
                    "label": "Acceleration start",
                    "description": "What is the acceleration start value",
                    "unit": "mm/s²",
                    "type": "float",
                    "default_value": 500.0,
                    "enabled": "acc_enable"
                },
                "acc_inc":
                {
                    "label": "Acceleration increment",
                    "description": "What is the acceleration increment",
                    "unit": "mm/s²",
                    "type": "float",
                    "default_value": 500.0,
                    "enabled": "acc_enable"
                },
                "lin_enable":
                {
                    "label": "Linear Advance",
                    "description": "Enable Linear Advande change",
                    "type": "bool",
                    "default_value": false
                },
                "lin_start":
                {
                    "label": "Linear Advance start",
                    "description": "What is the Linear Advance start value",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 0.0,
                    "enabled": "lin_enable"
                },
                "lin_inc":
                {
                    "label": "Linear Advance increment",
                    "description": "What is the Linear Advance increment",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 0.01,
                    "enabled": "lin_enable"
                },
                "junc_enable":
                {
                    "label": "Junction deviation",
                    "description": "Enable Junction deviation change",
                    "type": "bool",
                    "default_value": false
                },
                "junc_start":
                {
                    "label": "Junction deviation start",
                    "description": "What is the Junction deviation start value",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.013,
                    "enabled": "junc_enable"
                },
                "junc_inc":
                {
                    "label": "Junction deviation increment",
                    "description": "What is the Junction deviation increment",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.01,
                    "enabled": "junc_enable"
                },
                "temp_enable":
                {
                    "label": "Temperature deviation",
                    "description": "Enable temperature change",
                    "type": "bool",
                    "default_value": false
                },
                "temp_start":
                {
                    "label": "Temperature start",
                    "description": "What is the Temperature start value",
                    "unit": "°C",
                    "type": "int",
                    "default_value": 200,
                    "enabled": "temp_enable"
                },
                "temp_inc":
                {
                    "label": "Temperature increment",
                    "description": "What is the Temperature increment",
                    "unit": "°C",
                    "type": "int",
                    "default_value": 10,
                    "enabled": "temp_enable"
                }
            }
        }"""

    def execute(self, data):
        current_z = 0.
        current_l = 0.
        has_started = 0.
        
        height_switch_start = self.getSettingValueByKey("height_start")
        height_switch = self.getSettingValueByKey("height_inc")
        
        acc_enable = self.getSettingValueByKey("acc_enable")
        acc_start = self.getSettingValueByKey("acc_start")
        acc_inc = self.getSettingValueByKey("acc_inc")
        
        lin_enable = self.getSettingValueByKey("lin_enable")
        lin_start = self.getSettingValueByKey("lin_start")
        lin_inc = self.getSettingValueByKey("lin_inc")
        
        junc_enable = self.getSettingValueByKey("junc_enable")
        junc_start = self.getSettingValueByKey("junc_start")
        junc_inc = self.getSettingValueByKey("junc_inc")
        
        temp_enable = self.getSettingValueByKey("temp_enable")
        temp_start = self.getSettingValueByKey("temp_start")
        temp_inc = self.getSettingValueByKey("temp_inc")
        
        
        for layer in data: 
            lines = layer.split("\n")
            for line in lines:
                if has_started == 0 and line == ";LAYER:0":
                    has_started = 1
                if has_started == 1 and self.getValue(line, 'G') == 1 or self.getValue(line, 'G') == 0:
                    current_z = self.getValue(line, 'Z')
                    check_z = height_switch_start + height_switch * current_l
                    if current_z != None:
                        if current_z >= check_z:
                            prepend_gcode = ";TYPE:CUSTOM\n"
                            prepend_gcode += "; -- Change parameters at layer height (%.2f mm) --\n" % current_z
                            
                            if acc_enable == 1:
                                act_acc = acc_start + acc_inc * current_l
                                prepend_gcode += "M201 X%.2f Y%.2f\n" % (act_acc,act_acc)
                                
                            if lin_enable == 1:
                                lin_acc = lin_start + lin_inc * current_l
                                prepend_gcode += "M900 K%.2f\n" % lin_acc
                                
                            if junc_enable == 1:
                                junc_acc = junc_start + junc_inc * current_l
                                prepend_gcode += "M900 K%.2f\n" % junc_acc
                                
                            if temp_enable == 1:
                                temp_acc = temp_start + temp_inc * current_l
                                prepend_gcode += "M104 S%.2f\n" % temp_acc
                            
                            index = data.index(layer) 
                            layer = prepend_gcode + layer
                            data[index] = layer # Override the data of this layer with the modified data
                            current_l += 1
        return data