import pandas as pd
import numpy as np
import os

class FaceVectorEvaluator(object):
    SAME = "same"
    DIFF = "different"
    OUTPUT_DIR = "face_recogntion/conf_test"

    def __init__(self, nnModel, pairs_file = "./face_recognition/pairs.txt", dataset_folder = "./face_recognition/dataset/lfw",
                 threshold_list = None, offset_vals = None,
                 align_faces = True, apply_patching = False):

        # set defaults for list type parameters
        if threshold_list is None:
            self.threshold_list = np.around(np.linspace(0, 1, 5), 2).tolist()
        else:
            self.threshold_list = threshold_list

        if offset_vals is None or not offset_vals:
            self.offset_vals = [0.0, 0.05, 0.1, 0.2]
        else:
            self.offset_vals = offset_vals


        self.align_faces = align_faces
        self.apply_patching = apply_patching

        self.dataset_folder = dataset_folder
        self.pairs_file = pairs_file

        # these are the scaling sizes we consider given the used DNN model
        self.scale_sizes = [None, 256, 384, 512]

        """ for each descriptor computation call the nnModel will return:
                - descriptor, face detection confidence (in this order)
        """
        self.nnModel = nnModel

        # generate folds Data Frame
        self.folds_df = self._generate_lfw_folds()
        self.test_fold = self.folds_df.loc[1]
        self.unique_images = pd.concat([self.folds_df.loc[1]['img1_path'], self.folds_df.loc[1]['img2_path']]).unique()

        # define internal descriptor cache dictionaries for the different scale sizes - these will be refreshed at every change in parameter combinations
        self._descriptor_cache_none = {}
        self._descriptor_cache_256 = {}
        self._descriptor_cache_384 = {}
        self._descriptor_cache_512 = {}

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

    def _get_distance(self, vec1, vec2):
        """
        Returns the distance between two descriptor vectors (in this case the Euclidian distance)
        :param vec1: first normalized vector
        :param vec2: second normalized vector
        :return: The euclidian distance of the two vectors
        """
        return np.linalg.norm(vec1 - vec2)


    def _score(self, descriptor_cache, threshold):
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        distance_dict = {'img1' : [], 'img2' : [], 'distance' : []}

        for _, row in self.test_fold.iterrows():
            img1 = row['img1_path']
            img2 = row['img2_path']
            label = row['label']

            img1_desc = descriptor_cache.get(img1)
            img2_desc = descriptor_cache.get(img2)

            distance = self._get_distance(img1_desc, img2_desc)
            distance_dict['img1'].append(img1)
            distance_dict['img2'].append(img2)
            distance_dict['distance'].append(round(distance, 2))

            same = distance <= threshold
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

        score_dict = {}
        score_dict.update({"tp": tp, "fp": fp, "tn": tn, "fn": fn})
        score_dict['nr_pos'] = self.test_fold[self.test_fold['label'] == FaceVectorEvaluator.SAME].shape[0]
        score_dict['nr_neg'] = self.test_fold[self.test_fold['label'] == FaceVectorEvaluator.DIFF].shape[0]

        return (distance_dict, score_dict)


    def _populate_descriptors_cache(self, conf_dict, scale_size):
        desc_dict = None
        if scale_size is None:
            desc_dict = self._descriptor_cache_none
        elif scale_size == 256:
            desc_dict = self._descriptor_cache_256
        elif scale_size == 384:
            desc_dict = self._descriptor_cache_384
        else:
            desc_dict = self._descriptor_cache_512

        for _, img in self.unique_images.iterrows():
            img_desc = self.nnModel.get_descriptor(img = img, scale_size = scale_size, **conf_dict)
            desc_dict[img] = img_desc


    def _save_score(self, conf_dict, scale_size, threshold, distance_dict, score_dict):
        df_config = pd.DataFrame([(conf_dict['offset'], conf_dict['align'], conf_dict['patching'], scale_size, threshold)],
                                 columns = ['offset', 'align', 'patching', 'scale_size', 'threshold'])
        df_score = pd.DataFrame([(score_dict['tp'], score_dict['fp'], score_dict['tn'], score_dict['fn'], score_dict['nr_pos'], score_dict['nr_neg'])],
                                columns = ['tp', 'fp', 'tn', 'fn', 'nr_pos', 'nr_neg'])
        df_distance = pd.DataFrame.from_dict(distance_dict)

        filename = 'conf_{}_{}_{}_{}_{}.xlsx'.format(str(conf_dict['offset']), conf_dict['align'], conf_dict['patching'], scale_size, threshold)
        writer = pd.ExcelWriter(FaceVectorEvaluator.OUTPUT_DIR + os.sep + filename)

        df_config.to_excel(writer, 'Config')
        df_score.to_excel(writer, 'Score')
        df_distance.to_excel(writer, 'Distances')
        writer.save()


    def evaluate(self):
        import itertools

        if self.nnModel is None:
            raise ValueError("DNN Model is not allowed to be None!")

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

        """ Go through each configuration and:
                - first collect the descriptors for each unique image, for each possible scale size (including no scaling)
                - after each collection perform distance computations and save them to file
        """
        for conf_dict in conf_dict_list:
            ## flush descriptor caches
            self._descriptor_cache_none.clear()
            self._descriptor_cache_256.clear()
            self._descriptor_cache_384.clear()
            self._descriptor_cache_512.clear()

            ## compute new descriptors for this configuration and score them
            self._populate_descriptors_cache(conf_dict, None)
            for threshold in self.threshold_list:
                distance_dict, score_dict = self._score(self._descriptor_cache_none, threshold)
                self._save_score(conf_dict, None, threshold, distance_dict, score_dict)

            # descriptors for scale size 256
            self._populate_descriptors_cache(conf_dict, 256)
            for threshold in self.threshold_list:
                distance_dict, score_dict = self._score(self._descriptor_cache_256, threshold)
                self._save_score(conf_dict, 256, threshold, distance_dict, score_dict)

            # descriptors for scale size [256 + 384]
            self._populate_descriptors_cache(conf_dict, 384)
            descriptor_cache = dict((key, (self._descriptor_cache_256[key] + self._descriptor_cache_384[key]) / 2.0)
                                    for key in self._descriptor_cache_384.keys())
            for threshold in self.threshold_list:
                distance_dict, score_dict = self._score(descriptor_cache, threshold)
                self._save_score(conf_dict, 384, threshold, distance_dict, score_dict)

            # descriptors for scale size [256 + 384 + 512]
            self._populate_descriptors_cache(conf_dict, 512)
            descriptor_cache = dict((key, (self._descriptor_cache_256[key] + self._descriptor_cache_384[key] + self._descriptor_cache_512) / 3.0)
                                    for key in self._descriptor_cache_512.keys())
            for threshold in self.threshold_list:
                distance_dict, score_dict = self._score(descriptor_cache, threshold)
                self._save_score(conf_dict, 512, threshold, distance_dict, score_dict)
