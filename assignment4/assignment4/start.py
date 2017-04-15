import assignment3.coordinator as coordinator

mappers = ['idf_mapper.py','invindex_mapper.py', 'docs_mapper.py']
reducers = ['idf_reducer.py','invindex_reducer.py', 'docs_reducer.py']
job_paths = ['idf_jobs', 'invindex_jobs', 'docs_jobs']

mapper_path = './assignment4/mr_apps/'
reducer_path = './assignment4/mr_apps/'
job_path = './assignment4/'

for i in range(len(mappers)):
    coordinator.run(mapper_path + mappers[i], reducer_path + reducers[i], job_path + job_paths[i])

print("Finished")