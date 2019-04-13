import os
import shutil
import urllib.request
from ravenml.utils.local_cache import global_cache
import tarfile


def prepare_for_training(data_path, base_dir, arch_path):

    # create base dir if doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    # create a data folder within our base_directory
    os.makedirs(os.path.join(base_dir, 'data'))
    print('Created data folder')

    # copy object-detection.pbtxt from utilities and move into data folder
    pbtxt_file = os.path.join(data_path, 'label_map.pbtxt')
    shutil.copy(pbtxt_file, os.path.join(base_dir, 'data'))
    print('Placed label_map.pbtxt file inside data folder')

    # create models, model, eval, and train folders
    models_folder = os.path.join(base_dir, 'models')
    os.makedirs(models_folder)
    model_folder = os.path.join(models_folder, 'model')
    os.makedirs(model_folder)
    eval_folder = os.path.join(model_folder, 'eval')
    train_folder = os.path.join(model_folder, 'train')
    os.makedirs(eval_folder)
    os.makedirs(train_folder)
    print('Created models, model, train, eval folders')

    # create pipeline file based on a template and our desired path

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_path = os.path.join(cur_dir, 'pipeline_template.config')
    print('PIPELINE PATH', pipeline_path)
    with open(pipeline_path) as template:
        pipeline_contents = template.read()
    if base_dir.endswith('/') or base_dir.endswith(r"\\"):
        pipeline_contents = pipeline_contents.replace('<replace>', base_dir)
    else:
        if os.name == 'nt':
            pipeline_contents = pipeline_contents.replace('<replace>', base_dir + r"\\")
        else:
            pipeline_contents = pipeline_contents.replace('<replace>', base_dir + '/')
    pipeline_path = os.path.join(model_folder, 'pipeline.config')
    with open(pipeline_path, 'w') as file:
        file.write(pipeline_contents)
    print('Created pipeline.config file inside models/model/')

    # TODO: change to move all sharded chunks
    train_record = os.path.join(data_path, 'dev/standard/tf/train.record-00000-of-00001')
    test_record = os.path.join(data_path, 'dev/standard/tf/test.record-00000-of-00001')

    shutil.copy(train_record, os.path.join(base_dir, 'data'))
    shutil.copy(test_record, os.path.join(base_dir, 'data'))
    print("Copied records to data directory")

    # copy model checkpoints to our train folder
    checkpoint_folder = os.path.join(arch_path)
    checkpoint0_folder = os.path.join(cur_dir, 'checkpoint_0')
    # file1 = os.path.join(checkpoint_folder, 'checkpoint')

    file1 = os.path.join(checkpoint_folder, 'model.ckpt.data-00000-of-00001')
    file2 = os.path.join(checkpoint_folder, 'model.ckpt.index')
    file3 = os.path.join(checkpoint_folder, 'model.ckpt.meta')
    file4 = os.path.join(checkpoint0_folder, 'model.ckpt-0.data-00000-of-00001')
    file5 = os.path.join(checkpoint0_folder, 'model.ckpt-0.index')
    file6 = os.path.join(checkpoint0_folder, 'model.ckpt-0.meta')
    checkpoint_file = os.path.join(checkpoint0_folder, 'checkpoint')
    shutil.copy2(file1, train_folder)
    shutil.copy2(file2, train_folder)
    shutil.copy2(file3, train_folder)
    shutil.copy2(file4, train_folder)
    shutil.copy2(file5, train_folder)
    shutil.copy2(file6, train_folder)
    with open(checkpoint_file) as cf:
        checkpoint_contents = cf.read()
    checkpoint_contents = checkpoint_contents.replace('<replace>', train_folder)
    with open(os.path.join(train_folder, 'checkpoint'), 'w') as new_cf:
        new_cf.write(checkpoint_contents)
    print('Added model checkpoints to models/model/train folder')


def download_model_arch(model_name):

    print("Downloading model checkpoint...")
    url = 'http://download.tensorflow.org/models/object_detection/%s.tar.gz' %(model_name)
    cache_path = global_cache.path
    archs_path = os.path.join(cache_path, 'bbox_model_archs')
    os.makedirs(archs_path, exist_ok=True)

    tar_name = url.split('/')[-1]
    model_path = os.path.join(archs_path, tar_name)
    urllib.request.urlretrieve(url, model_path)
    
    print("Untarring model checkpoint...")
    if (model_path.endswith("tar.gz")):
        tar = tarfile.open(model_path, "r:gz")
        tar.extractall(path=archs_path)
        tar.close()

    untarred_path = os.path.join(archs_path, model_name)


    return untarred_path
