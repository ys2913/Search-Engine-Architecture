import argparse


class Parser:
    def getargs(self):
        parser = argparse.ArgumentParser(description='Coordinator')
        parser.add_argument('--mapper_path', action='store', default='wordcount/mapper.py',
                            help='Mapper path')
        parser.add_argument('--reducer_path', action='store', default='wordcount/reducer.py',
                            help='Reducer path')
        parser.add_argument('--job_path', action='store', default='fish_jobs',
                            help='job path')
        parser.add_argument('--num_reducers', type=int, default=1, metavar='N',
                            help='Number of reducers required')
        args = parser.parse_args()
        return args
