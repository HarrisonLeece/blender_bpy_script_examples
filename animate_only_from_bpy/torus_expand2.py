import bpy
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


def clear_all_data():
    for curve in bpy.data.curves:
        if curve.users == 0:
            bpy.data.curves.remove(curve)
            
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

if __name__ == "__main__":
    clear_all_data()
    
    out_dir = "/media/harrison/the_ark/blender_renders/snare_torus/"
    pattern = ".png"

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.scene.render.film_transparent = True #For transparent Alpha background, switch to True
    
    mat1 = newShader("purple","emission", 0.21176,.0039215, 0.2470588, 1)
    
    str_frm = 16; end_frm = 30; #integers
    
    bpy.context.scene.frame_start = str_frm
    bpy.context.scene.frame_end = end_frm

    bpy.context.scene.eevee.use_bloom = False #Loooooool

    start = 0.117; target = 1.36
    num_frames = int(end_frm - str_frm)
    
    adj_lin = np.linspace(start, target, end_frm+1)
    
    
    mult = np.linspace(1,0,num_frames+1)
    
    
    rng = np.linspace(str_frm,end_frm,num_frames+1)
    print(rng)
    #exponential_adjust = map_to_exponent(rng)
    for i in rng:
        i = int(i) - str_frm
        #clear all objects
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj,do_unlink=True)
            
        #all objects cleared
        
        bpy.ops.curve.spirals(spiral_type='TORUS', turns=1, steps=360, radius=3.31, dif_z=0, dif_radius=-5.49,  inner_radius=0.01, dif_inner_radius=0.0, cycles=0+adj_lin[-1], curves_number=239, touch=False)
        
        bpy.context.object.data.bevel_depth = 0.0092*mult[i]
        
        mat2 = newShader("fade","emission", 0.21176,.0039215, 0.2470588, 1)
        bpy.data.collections['Collection'].objects[0].active_material = bpy.data.materials["purple"]
        

        #https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
        scn = bpy.context.scene
        
        cam1 = bpy.data.cameras.new("Camera")
        cam1.lens = 71
        
        cam_obj1 = bpy.data.objects.new("Camera", cam1)
        cam_obj1.location = (0, -.4, 33.309)
        cam_obj1.rotation_euler = rotation=(0.0, 0.0, 0.405)
        scn.collection.objects.link(cam_obj1)
        
        scn.camera = bpy.data.objects['Camera']
        
        render_image_indexed(out_dir, pattern, i+str_frm, end_frm)
