import bpy
import sys
import math
import numpy as np
import random

#SoundInfo class

class SoundInfo:

    def __init__(self):
        self.fps =0;
        self.samp_freq = 0;
        self.start_pad = 0;
        self.end_pad = 0;
        self.wave_length = 0;
        self.num_psd = 0;
        self.beat_mat_size = 0;

        self.beat_mat = [];
        self.waveform = []; #A list
        self.psd_matrix = []; # A list of lists
        #For the future
        self.bass_fundamental = 0


    def import_flg(self, file_name):
        with open(file_name, 'r') as flg:
            #Get the header from read line and store them to member variable
            self.fps = int(flg.readline())
            self.samp_freq = int(flg.readline())
            self.start_pad = int(flg.readline())
            self.end_pad = int(flg.readline())
            self.wave_length = int(flg.readline())
            self.num_psd = int(flg.readline())
            self.beat_mat_size = int(flg.readline())

            temp = []; #holds lists of temporary information
            #read beat matrix
            for i in range(int(self.beat_mat_size)+1):
                temp = flg.readline();
                if (temp[0] == "#"):
                    print(temp)
                self.beat_mat.append(self.remove_commas(temp))
            #read waveform comma separated variable line into temp
            temp = flg.readline()
            self.waveform = self.remove_commas(temp)
            temp = flg.readline() #should read #EndWaveform
            print(type(temp)); print(temp);
            if(temp[0] != "#"):
                print(temp); print("ERROR: expected #EndWaveform");
                sys.exit()
            print(temp); #Should be #EndWaveform printed to console

            #Get the PSD data
            for line in flg.readlines():
                if (line[0] == "#"):
                    print(line)
                    break;
                temp = self.remove_commas(line)
                self.psd_matrix.append(temp)



    def remove_commas(self, comma_list):
        temp = []; output = [];
        for element in comma_list:
            if (element != ","):
                temp.append(element)
            else:
                output.append(float(''.join(temp)))
                temp=[]; #flush temp so a new number can be added
        return output
    
###End Class



### Performance utilities

def render_image_indexed(output_dir, out_type, step, ani_length):
    string_order= int(np.ceil(np.log10(ani_length+1)))
    index_order = int(np.ceil(np.log10(step+1)))
    out_string = ""
    
    for i in range(string_order-index_order):
        out_string += "0"
    if (step != 0):
        out_string += str(int(step))
    bpy.context.scene.render.filepath = output_dir+out_string
    bpy.ops.render.render(write_still = True)


### End performance utilities

def map_to_exponent_large2small(input_vector, start, end):
    output = []
    p = np.linspace(0,1.011,len(input_vector))
    #max_value = -100*np.e**(3.39*0-8) + 1.034
    max_value = start
    #-1*(100*np.e**(3.39x - 8))+1
    for i in range(len(input_vector)):
        k = max_value
        out = round((k*((-100*np.e**(3.39*p[i] - 8))+1.034)),8) + end
        print(out)
        output.append(out)
    return output

def clear_all_data():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
        else:
            obj.select_set(False)
        bpy.ops.object.delete()
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

#https://vividfax.github.io/2021/01/14/blender-materials.html
def newMaterial(id):

    mat = bpy.data.materials.get(id)

    if mat is None:
        mat = bpy.data.materials.new(name=id)

    mat.use_nodes = True

    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat

def newShader(id, type, r, g, b, a):

    mat = newMaterial(id)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new(type='ShaderNodeOutputMaterial')

    if type == "diffuse":
        shader = nodes.new(type='ShaderNodeBsdfDiffuse')
        nodes["Diffuse BSDF"].inputs[0].default_value = (r, g, b, a)

    elif type == "emission":
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs[0].default_value = (r, g, b, a)
        nodes["Emission"].inputs[1].default_value = 1

    elif type == "glossy":
        shader = nodes.new(type='ShaderNodeBsdfGlossy')
        nodes["Glossy BSDF"].inputs[0].default_value = (r, g, b, a)
        nodes["Glossy BSDF"].inputs[1].default_value = 0

    links.new(shader.outputs[0], output.inputs[0])

    return mat

def render_image_indexed(output_dir, out_type, step, ani_length):
    string_order= int(np.ceil(np.log10(ani_length+1)))
    index_order = int(np.ceil(np.log10(step+1)))
    out_string = ""
    
    for i in range(string_order-index_order):
        out_string += "0"
    if (step != 0):
        out_string += str(int(step))
    bpy.context.scene.render.filepath = output_dir+out_string
    bpy.ops.render.render(write_still = True)
    
def wave_interpolation(length=1, height=1, floor = 0):
    x_vals = np.linspace(0,1,length)
    output = []
    num = floor
    for x in x_vals:
        if (x < 2/9):
            num = -40.5811/2 * x**2 + 9.009*x + 0
        else:
            num = 3.3043/2 * x**2 - 3.3043*x + 1.652115
        output.append(num)
    return output

def sine_interpolation(length=1, height=1, floor = -1):
    x_vals = np.linspace(0,1,length)
    output = []
    for x in x_vals:
        num = math.sin(x*2*3.1415)
        output.append(num)
    return output

if __name__ == "__main__":
    
    test = SoundInfo()
    test.import_flg("/home/harrison/Documents/work/programming/_project_avalanche/flag_files/output.flg")
    print(test.beat_mat)
    start_frm = 0; end_frm = test.beat_mat_size;
    
    bpy.context.scene.frame_start = start_frm
    bpy.context.scene.frame_end = end_frm-1

    #animation parameters
    kick_wait = 0 ; kick_max = 10; kick_filter = int(np.floor((2/9)*kick_max)+1); #2/9
    #snare_wait = 0; snare_max = 30; snare_filter = int(np.floor((2/9)*snare_max)+1);
    wave_list = wave_interpolation(length = kick_max, height = 1, floor = 0)
    sine_list = sine_interpolation(length = kick_max)
    
    #What items to animate
    dopa_ring = bpy.data.node_groups["Geometry Nodes.001"].nodes["Translate Instances"].inputs[2]
    #update default_value[2] for sero, default_value[1] for dopa
    sero_ring = bpy.data.node_groups["Geometry Nodes"].nodes["Translate Instances"].inputs[2]
    brain_shade = bpy.data.materials["Default OBJ"].node_tree.nodes["Mix"].inputs[0]


    
    #reset drop orbital speed change
    dopa_orbit = bpy.data.node_groups["Geometry Nodes.001"].nodes["Math.002"].inputs[1]
    sero_orbit = bpy.data.node_groups["Geometry Nodes"].nodes["Math.001"].inputs[1]
    outer_sero =  bpy.data.node_groups["Geometry Nodes.002"].nodes["Math.001"].inputs[1]
    
    dopa_orbit.default_value = 1 #dopa
    sero_orbit.default_value = 1 #sero
    outer_sero.default_value = 0.097 #outer_sero
    
    dopa_orbit.keyframe_insert(data_path='default_value', frame = 0)
    sero_orbit.keyframe_insert(data_path='default_value', frame = 0)
    outer_sero.keyframe_insert(data_path='default_value', frame = 0)

    drop_frame = 900

    #path = shader.path_from_id('default_value')
    
    for frame_num, vec in enumerate(test.beat_mat):
        #####Kick logic
        #if kick detected
        if (test.beat_mat[frame_num][0]==1 or kick_wait > 0):
            if (kick_wait == 0): #if no kick has been detected recently, detect the kick and start the animation
                kick_wait = kick_max;
                print("Kick detected on frame: " + str(frame_num) +" blocking for: " + str(kick_filter) + " frames")
                for index, value in enumerate(sine_list):
                    dopa_ring.default_value[1] = 1*value
                    sero_ring.default_value[2] = 1*value
                    wave_value = wave_list[index]
                    brain_shade.default_value = wave_value
                    dopa_ring.keyframe_insert(data_path='default_value', frame = frame_num+index)
                    sero_ring.keyframe_insert(data_path='default_value', frame = frame_num+index)
                    brain_shade.keyframe_insert(data_path='default_value', frame = frame_num+index)
                    
                    
            elif (test.beat_mat[frame_num][0]==1 and kick_wait <= (kick_max-kick_filter)): #reset the animation to the end of the kick filter
                print("Another kick detected while animation playing on frame: " + str(frame_num) + "; past wait: " + str(kick_wait) +"; blocking for: " + str(kick_filter) + " frames")
                print("Restarting animation of current frame to the peak " + str(frame_num+kick_max))
                kick_wait = kick_max - kick_filter
                for index, value in enumerate(sine_list):
                    if (index <= kick_filter):
                        #skip the first <snare_filter> values to prevent coming up twice before peak
                        pass
                    else:
                        dopa_ring.default_value[1] = 1*value
                        sero_ring.default_value[2] = 1*value
                        wave_value = wave_list[index]
                        brain_shade.default_value = wave_value
                        dopa_ring.keyframe_insert(data_path='default_value', frame = frame_num+index-kick_filter)
                        sero_ring.keyframe_insert(data_path='default_value', frame = frame_num+index-kick_filter)
                        brain_shade.keyframe_insert(data_path='default_value', frame = frame_num+index-kick_filter)
                    
            
            
            kick_wait+= -1 #kick wait will always be greater than 0 when this line is reached
            
        #reset to 0
        if (kick_wait == 0):
            dopa_ring.default_value[1] = sine_list[0]
            sero_ring.default_value[2] = sine_list[0]
            brain_shade.default_value = wave_list[0]
        #This doesnt have to be in an if statement, but fuck it, why not
        if (frame_num == drop_frame):
            dopa_orbit.keyframe_insert(data_path='default_value', frame = drop_frame-1)
            sero_orbit.keyframe_insert(data_path='default_value', frame = drop_frame-1)
            outer_sero.keyframe_insert(data_path='default_value', frame = drop_frame-1)
            
            dopa_orbit.default_value = 2.32
            sero_orbit.default_value = 1.337
            outer_sero.default_value = 0.43
            dopa_orbit.keyframe_insert(data_path='default_value', frame = end_frm)
            sero_orbit.keyframe_insert(data_path='default_value', frame = end_frm)
            outer_sero.keyframe_insert(data_path='default_value', frame = end_frm)
            
            
            
            

            
        ####End kick logic 
