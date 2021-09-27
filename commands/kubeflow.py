from commands.slash_command import SlashCommand
from flask import request
from message import KubeflowMessage
from google_drive_downloader import GoogleDriveDownloader as gdd
import re

import kfp
import os


class KubeflowCommand(SlashCommand):
    def __init__(self, bot):
        self.bot_client = bot.client
        self.cookies = os.environ["COOKIES"]
        self.uri = os.environ['URI']
        self.namespace = os.environ['NAMESPACE']
        self.kube_client = kfp.Client(host=f'http://{self.uri}/pipeline', namespace=self.namespace, cookies=self.cookies)
        self.kube_info = KubeflowMessage(self.bot_client)

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        text = data.get("text", "").lstrip()
        channel = f"@{user}"

        if text.startswith('list-experiments'):
            list_experiments = self.kube_client.list_experiments(namespace=self.namespace)
            url = f'http://{self.uri}/_/pipeline/?ns={self.namespace}#/experiments'
            res = []

            for i, experiment in enumerate(list_experiments.experiments):
                if i > 5: break
                res.append(f'*id*: {experiment.id} \n\n *name*: {experiment.name}')
            
            res = '\n\n'.join(res)

            self.kube_info.send_message(channel, f"*list of experiments*", res, url)
        
        elif text.startswith('list-pipelines'):
            list_pipelines = self.kube_client.list_pipelines()
            url = f'http://{self.uri}/_/pipeline/?ns={self.namespace}#/pipelines'
            res = []

            for i, pipeline in enumerate(list_pipelines.pipelines):
                if i > 5: break
                res.append(f'*id*: {pipeline.id} \n\n *name*: {pipeline.name}')
            
            res = '\n\n'.join(res)

            self.kube_info.send_message(channel, f"*list of pipelines*", res, url)

        elif text.startswith('upload-pipeline'):
            args = text.split('--')
            file_id, name = args[-1].split('=')[-1].lstrip().rstrip(), args[-2].split('=')[-1].lstrip().rstrip()
            gdd.download_file_from_google_drive(file_id=file_id, dest_path='./temp/file.tar.gz', overwrite=True)

            pipeline = self.kube_client.upload_pipeline('./temp/file.tar.gz', name)
            res = f"*id*: {pipeline.id} \n\n *name*: {pipeline.name}"
            url = f'http://{self.uri}/_/pipeline/?ns={self.namespace}#/pipelines/details/{pipeline.id}'
            self.kube_info.send_message(channel, f"*Finished uploading a pipeline*", res, url)
        
        elif text.startswith('run-pipeline'):
            experiment_id, name, pipeline_id = re.findall(r'experiment=(\w+-\w+-\w+-\w+-\w+)', text), re.findall(r'experiment=(\w+)', text), re.findall(r'pipeline=(\w+-\w+-\w+-\w+-\w+)', text)

            run = self.kube_client.run_pipeline(experiment_id, name, pipeline_id=pipeline_id)
            res = f"*id*: {run.id} \n\n *name*: {run.name}"
            url = f'http://{self.uri}/_/pipeline/?ns={self.namespace}#/runs/details/{run.id}'
            self.kube_info.send_message(channel, f"*Running a pipeline*", res, url)
