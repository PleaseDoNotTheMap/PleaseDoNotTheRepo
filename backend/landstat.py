import json
import logging

logger = logging.getLogger('landstat.api')


class API:
    def __init__(self, session):
        self.stac_server = None
        self.search_endpoint = None
        self.url = 'https://landsatlook.usgs.gov/stac-server'
        self.session = session

    async def start(self):
        self.stac_server = json.loads(await (await self.session.get(self.url)).text())
        self.search_endpoint = self.get_links('search')[0]

        logger.debug(f"Stac Version: {self.stac_server['stac_version']}")
        return self

    def get_links(self, rel):
        return [link['href'] for link in self.stac_server['links'] if
                link['rel'] == rel]

    async def search(self, params):
        response = json.loads(
            await (await self.session.post(self.search_endpoint, json=params)).text())
        results = response['features']

        features = []
        for feature in results:
            new_feature = {
                'id': feature['id'],
                'date': feature['properties']['datetime'],
                'platform': feature['properties']['platform'],
                'cloudCover': feature['properties']['eo:cloud_cover']
            }

            assets = []
            for a in feature['assets']:
                try:
                    logger.debug(f"Asset: {feature['assets'][a]['title']}")
                    logger.debug(f"Type: {feature['assets'][a]['type']}")
                    logger.debug(f"Description: {feature['assets'][a]['description']}")
                    logger.debug(f"Role: {feature['assets'][a]['roles']}")
                    logger.debug(
                        f"S3 URL: {feature['assets'][a]['alternate']['s3']['href']}\n")
                    assets.append({
                        'title': feature['assets'][a]['title'],
                        'type': feature['assets'][a]['type'],
                        'role': feature['assets'][a]['roles'],
                        'url': feature['assets'][a]['alternate']['s3']['href']
                    })
                except Exception:
                    logger.debug(f"Role: {feature['assets'][a]['roles']}")
                    logger.debug(f"URL: {feature['assets'][a]['href']}\n")
                    assets.append({
                        'role': feature['assets'][a],
                        'url': feature['assets'][a]['href']
                    })
                    continue

            new_feature['assets'] = assets
            features.append(new_feature)

        return features
