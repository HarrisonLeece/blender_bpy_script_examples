import bpy 
import numpy as np
import math
import random
import mathutils
from math import radians

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

    #for block in bpy.data.materials:
    #    if block.users == 0:
    #        bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)

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
            
if __name__ == "__main__":
    #clear all objects
    #for obj in bpy.data.objects:
    #    bpy.data.objects.remove(obj,do_unlink=True)
    #all objects cleared
    clear_all_data()
    
    out_dir = "/media/harrison/the_ark/blender_renders/demo_timer/"
    pattern = ".png"
    
    ### Sound data import
    data = SoundInfo()
    data.import_flg("/home/harrison/Documents/work/programming/_project_avalanche/flag_files/output.flg")
    ###
    
    
    #Create a dummy object off screen to create material
    #bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(64.08, 46.67, 0), scale=(1, 1, 1))
    
    #Render settings
    bpy.context.scene.render.resolution_y = 117
    bpy.context.scene.render.resolution_x = 3840
    bpy.context.scene.render.film_transparent = True
    #End render setting
    
    ###Camera info
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(78.397, .19, 428.11), rotation=(0, 0, 0), scale=(1, 1, 1))
    bpy.context.object.data.lens = 97
    
    ###End camera info
    
    ##### Lighting info
    #bpy.ops.object.light_add(type='SUN', align='WORLD', location=(64.08, 0, 100), scale=(1, 1, 1))
    #####
    
    #### Materials Start - Set within the UI and assign variables here
    
    mat = bpy.data.materials['Transparent']
    #### Materials end
    #### Track Data
    track_time = 24 #track time in seconds
    fps = 60
    num_frames = data.beat_mat_size
    #### Track Data end
    ##Animation data
    animation_len = 4; #frames
    animation_count_down = 0;
    
    num_tris = 351; 
    
    adjustment_factor = (num_frames - animation_len) % num_tris + animation_len
    
    frames_per_tri = (num_frames-adjustment_factor)/num_tris
    
    #frames_per_tri = np.floor((num_frames-animation_len)/num_tris); #frames per tri should be an int
    rem_frames = (num_frames/num_tris)%frames_per_tri
    
    flip_delta_60 = radians(60/animation_len); flip_delta_180 = radians(180/animation_len);
    
    #reset cursor location
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    #
    ##Cursor movement parameters
    cursor_location = 0; cursor_delta = 1.78; 
    ##
    rotation = 0;
    ####First triangle init
    bpy.ops.curve.simple(align='WORLD', location=(0, -1.04, 0), rotation=(0, 0, 0), Simple_Type='Polygon', shape='2D', use_cyclic_u=True)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.data.objects[-1].active_material = mat; #Set material to the correct material
    last_generated = 2
    ####
    #
    skip_number = 0
    #
    render_image_indexed(out_dir, pattern, 0, num_frames)
    print(num_frames)
    for frame in range(num_frames-1):
        
        if (frame%frames_per_tri == 0 and (num_frames-frame)>adjustment_factor):
            bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
            #bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            last_generated +=1 
            if (last_generated == 4):
                last_generated = 0
            animation_count_down = animation_len
            bpy.data.objects[-1].active_material = mat; #Set material to the correct material
        
        #Animate and control origin
        if (animation_count_down > 0 ):
            #if still animating triangle motion, 
            if (last_generated == 1):
                bpy.data.objects[-1].rotation_euler.rotate_axis('Z',-flip_delta_60)
            if (last_generated == 3):
                bpy.data.objects[-1].rotation_euler.rotate_axis('Z', flip_delta_60)
                #if we have already completed the last rotation in the animation, reset the origin point
                if (animation_count_down == 1):
                    #move 3d cursor
                    cursor_location = cursor_location + cursor_delta
                    bpy.context.scene.cursor.location = (cursor_location, 0.0, 0.0)
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            if (last_generated == 0):
                bpy.data.objects[-1].rotation_euler.rotate_axis('Z', -flip_delta_60)
            if (last_generated == 2):
                bpy.data.objects[-1].rotation_euler.rotate_axis('Z', flip_delta_180)
                           
            #Decrement countdown and reset rotation when appropriate
        animation_count_down = animation_count_down - 1
        print('Rending frame: '); print(frame)
        #if (frame>skip_number):
        render_image_indexed(out_dir, pattern, frame+1, num_frames)
            
