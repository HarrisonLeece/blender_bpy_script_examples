import bpy
import os
import numpy as np


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

def map_to_exponent(input_vector):
    output = []
    max_value = 10*np.e**(1-2.3)-1
    for i in range(len(input_vector)):
        x = i/len(input_vector)
        current_value = 10*np.e**(x-2.3)-1
        output.append(input_vector[i]*current_value/max_value)
    return output

if __name__ == "__main__":
    out_dir = "/mnt/dbd2c981-2b98-4187-8484-0ecabc9ba20b/mass_media/blender_renders/others_works/Nightfall/torus_animation_generate/"
    pattern = ".png"
    
    bpy.ops.material.new()
    bpy.data.materials["Material"].node_tree.nodes["Emission"].inputs[0].default_value = (0.0215682, 0.15627, 1, 1)

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.scene.render.film_transparent = False #For transparent Alpha background, switch to True

    end_frm = 600
    bpy.context.scene.frame_end = end_frm

    bpy.context.scene.eevee.use_bloom = True

    start = 33.333; target = 1.337
    num_frames = target-start
    
    adj_lin = np.linspace(start, target, end_frm+1)
    adj_exp = map_to_exponent(adj_lin)
    
    
    rng = np.linspace(0,end_frm,end_frm+1)
    #exponential_adjust = map_to_exponent(rng)
    for i in rng:
        #clear all objects
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj,do_unlink=True)
            
        #all objects cleared
        
        bpy.ops.curve.spirals(spiral_type='TORUS', turns = 137, steps=39, radius=2.56, dif_z=0, dif_radius=1.29, inner_radius=0, dif_inner_radius=adj_lin[int(i)], cycles=2.47, curves_number=171)
        #bpy.ops.transform.resize(value=(1.09358, 1.09358, 1.09358), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.transform.resize(value=(-0.73, -0.73, -0.73), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)


        bpy.context.object.data.bevel_depth = 0.17

        bpy.data.collections['Collection'].objects[0].active_material = bpy.data.materials["Material"]
        

        # https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
        scn = bpy.context.scene
        
        cam1 = bpy.data.cameras.new("Camera")
        cam1.lens = 50
        
        cam_obj1 = bpy.data.objects.new("Camera", cam1)
        cam_obj1.location = (-697, -654, 249.35)
        cam_obj1.rotation_euler = rotation=(1.32514, 0.0, -0.817552)
        scn.collection.objects.link(cam_obj1)
        
        scn.camera = bpy.data.objects['Camera']
        
        render_image_indexed(out_dir, pattern, i, end_frm)
