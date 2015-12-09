import pandas as pd
import numpy as np

class FaceVectorEvaluator(object):
    SAME = "same"
    DIFF = "different"

    def __init__(self, nnModel, pairs_file = "./face_recognition/pairs.txt", dataset_folder = "./face_recognition/dataset/lfw",
                 threshold_list = None, offset_vals = None, scale_sizes = None,
                 align_faces = None, apply_patching = None):

        # set defaults for list type parameters
        if threshold_list is None:
            self.threshold_list = np.around(np.linspace(0, 1, 5), 2).tolist()
        else:
            self.threshold_list = threshold_list

        if offset_vals is None or not offset_vals:
            self.offset_vals = [0.0, 0.05, 0.1, 0.2]
        else:
            self.offset_vals = offset_vals

        if scale_sizes is None or not scale_sizes:
            self.scale_sizes = [256, 384, 512]
        else:
            self.scale_sizes = scale_sizes

        self.align_faces = align_faces
        self.apply_patching = apply_patching

        self.dataset_folder = dataset_folder
        self.pairs_file = pairs_file

        """ for each descriptor computation call the nnModel will return:
                - descriptor, face detection confidence (in this order)
        """
        self.nnModel = nnModel

        # generate folds Data Frame
        self.folds_df = self._generate_lfw_folds()

        # define internal descriptor cache dict - this will be refreshed at every change in parameter combinations
        self.descriptor_cache = {}

    def _generate_lfw_folds(self):
        import os

        # open pairs file and read content
        content = None
        with open(self.pairs_file) as f:
            content = [x.strip('\n') for x in f.readlines()]

        if content:
            nr_folds, fold_class_size = map(int, content[0].split())
            fold_size = 2 * fold_class_size

            index_list = []
            df_list = []

            for idx in range(0, nr_folds):
                # the first fold_class_size elements are the "same" pictures
                for i in range(0, fold_class_size):
                    elems = content[idx * fold_size + i + 1].split()
                    img1_name = elems[0] + "_" + str(elems[1]).zfill(4)
                    img2_name = elems[0] + "_" + str(elems[2]).zfill(4)

                    index_list.append((idx + 1))
                    df_list.append([os.path.abspath(self.dataset_folder + os.path.sep + img1_name + ".jpg"),
                                    os.path.abspath(self.dataset_folder + os.path.sep + img2_name + ".jpg"),
                                    "same"])

                for i in range(fold_class_size, fold_size):
                    elems = content[idx * fold_size + i + 1].split()
                    img1_name = elems[0] + "_" + str(elems[1]).zfill(4)
                    img2_name = elems[2] + "_" + str(elems[3]).zfill(4)

                    index_list.append((idx + 1))
                    df_list.append([os.path.abspath(self.dataset_folder + os.path.sep + img1_name + ".jpg"),
                                    os.path.abspath(self.dataset_folder + os.path.sep + img2_name + ".jpg"),
                                    "different"])

            return pd.DataFrame(df_list, columns = ['img1_path', 'img2_path', 'label'], index = index_list)

        else:
            raise ValueError("Provided pairs file does not have corresponding format!")


    def _normalize(self, vec):
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec

        return vec / norm


    def _is_same(self, vec1, vec2, threshold):
        """
        Returns whether the two vectors are the same or not, based on a thresholded euclidian distance
        :param vec1: first normalized vector
        :param vec2: second normalized vector
        :param threshold: double value for threshold
        :return: True if the vectors are the same (below the given threshold), False otherwise
        """
        distance = np.linalg.norm(vec1 - vec2)
        return distance <= threshold

    def _score_fold(self, fold, params):
        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for _, row in fold.iterrows():
            img1 = row['img1_path']
            img2 = row['img2_path']
            label = row['label']

            img1_desc = self.descriptor_cache.get(img1)
            img2_desc = self.descriptor_cache.get(img2)

            if not img1_desc:
                img1_desc = self.nnModel.get_descriptor(img1, params)
                self.descriptor_cache[img1] = img1_desc

            if not img2_desc:
                img1_desc = self.nnModel.get_descriptor(img1, params)
                self.descriptor_cache[img1] = img2_desc

            same = self._is_same(img1_desc, img2_desc, params['threshold'])
            if label == FaceVectorEvaluator.SAME:
                if same:
                    tp += 1
                else:
                    fn += 1
            else:
                if same:
                    fp += 1
                else:
                    tn += 1

        result_dict = {}.update(params)
        result_dict.update({"tp": tp, "fp": fp, "tn": tn, "fn": fn})
        result_dict['nr_pos'] = fold[fold['label'] == FaceVectorEvaluator.SAME].shape[0]
        result_dict['nr_neg'] = fold[fold['label'] == FaceVectorEvaluator.DIFF].shape[0]

        return result_dict


    def evaluate(self):
        import itertools

        # generate configuration options list
        options_list = [self.offset_vals]

        if self.align_faces is None:
            options_list.append([True, False])
        else:
            options_list.append([self.align_faces])

        if self.apply_patching is None:
            options_list.append([True, False])
        else:
            options_list.append([self.apply_patching])

        # generate all parameter combinations
        conf_combinations = itertools.product(*options_list)
        conf_dict_list = [{'offset': x[0], 'align': x[1], 'patching': x[2]} for x in conf_combinations]


        