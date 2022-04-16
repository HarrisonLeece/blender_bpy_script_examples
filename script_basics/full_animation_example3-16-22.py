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

def create_plane(number, position):
    return false

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
    clear_all_data() #Clear all data
    
    out_dir = "/mnt/dbd2c981-2b98-4187-8484-0ecabc9ba20b/mass_media/blender_renders/tests/topology_glow/"
    pattern = ".png"

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.scene.render.film_transparent = False #For transparent Alpha background, switch to True

    end_frm = 0
    bpy.context.scene.frame_end = end_frm

    bpy.context.scene.eevee.use_bloom = False #Loooooool


    
    
    rng = np.linspace(0,end_frm,end_frm+1)
    #exponential_adjust = map_to_exponent(rng)
    for i in rng:
        i = int(i)
        #clear all objects
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj,do_unlink=True)
        #all objects cleared
        
        #as an example, create a plane with hills
        bpy.ops.mesh.primitive_plane_add(size=300, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.mesh.subdivide(number_cuts=64)
        bpy.ops.object.mode_set(mode="OBJECT")
        
        
        mat1 = newShader("black","emission", 0,0,0, 1)
        bpy.context.active_object.data.materials.append(mat1)
        
        bpy.ops.object.modifier_add(type='DISPLACE')
        disp=bpy.context.object.modifiers[-1]
        disp.strength = 64.6
        disp.mid_level = 0
        bpy.ops.texture.new()
        tex1 = bpy.data.textures[-1]
        tex1.type = 'CLOUDS'
        bpy.data.textures[-1].noise_scale = 43
        bpy.data.textures[-1].noise_depth = 1
        disp.texture = tex1
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        
        bpy.data.objects['Plane'].active_material = bpy.data.materials["black"]
        
        mat2 = newShader("contour","emission", 255/255,137/255,0, 1)
        
        startr = 255; endr = 202;
        startg = 137; endg = 0;
        startb = 0; endb = 175;
        
        num_planes = 75
        rng = np.linspace(0,(num_planes-1),num_planes)
        r_arr = np.linspace(startr/255, endr/255, num_planes)
        g_arr = np.linspace(startg/255, endg/255, num_planes)
        b_arr = np.linspace(startb/255, endb/255, num_planes)
        for i in rng:
            i = int(i)
            print(i)
            bpy.ops.mesh.primitive_plane_add(size=200, enter_editmode=False, align='WORLD', location=(0, 0, .75*i), scale=(1, 1, 1))
            pln = bpy.data.objects[-1]
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].thickness = .000001
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["Plane"]
            bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
            bpy.context.object.modifiers["Boolean"].solver = 'EXACT'
            bpy.data.objects[-1].select_set(True)
            bpy.ops.object.convert(target='CURVE')
            if (bpy.context.object.type == "CURVE"):
                bpy.context.object.data.bevel_depth = 0.0043
                mat3 = newShader("contour"+str(i),"emission", r_arr[i],g_arr[i],b_arr[i], 1)
                bpy.context.active_object.data.materials.append(mat3)
            else:
                print('Plane did not form curve.')
                bpy.ops.object.delete()
            bpy.data.objects[-1].select_set(False)
            
        
        

        #bpy.context.object.data.bevel_depth = 0.0092


        
        # https://blender.stackexchange.com/questions/151319/adding-camera-to-scene
        scn = bpy.context.scene
        
        cam1 = bpy.data.cameras.new("Camera")
        cam1.lens = 50
        
        cam_obj1 = bpy.data.objects.new("Camera", cam1)
        cam_obj1.location = (53.204,-52.856,27.406)
        cam_obj1.rotation_euler = rotation=(83.1*3.1415/180, 0.0, 43.5*3.1415/180)
        scn.collection.objects.link(cam_obj1)
        
        scn.camera = bpy.data.objects['Camera']
        
        #hide any objecs not to be rendered
        #bpy.data.objects['Plane'].hide_render = True
        
        #render_image_indexed(out_dir, pattern, i, end_frm)
