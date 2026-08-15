from cffconvert.lib.cff_1_x_x.authors.zenodo import ZenodoAuthor
from cffconvert.lib.cff_1_x_x.zenodo import ZenodoObjectShared as Shared


class ZenodoObject(Shared):

    supported_cff_versions = [
        "1.3.0"
    ]

    def add_contributors(self):
        contributors = []
        for c in self.cffobj.get("contributors", []):
            # contributors are generated in the same way as authors, hence just
            # call ZenodoAuthor's contructor with the cff contributor object
            contributor = ZenodoAuthor(c).as_dict()
            if contributor is None or contributor.get("name") is None:
                continue
            contributor.update({"type": "Other"})
            contributors.append(contributor)
        if len(contributors) > 0:
            self.contributors = contributors
        return self

    def add_creators(self):
        authors_cff = self.cffobj.get("authors", [])
        creators_zenodo = [ZenodoAuthor(a).as_dict() for a in authors_cff]
        if any(creator is None or creator.get("name") is None for creator in creators_zenodo):
            raise ValueError("Zenodo requires every creator to have a name.")
        self.creators = creators_zenodo
        return self

    def add_license(self):
        license_value = self.cffobj.get("license")
        if isinstance(license_value, list):
            if len(license_value) > 1:
                raise ValueError("Zenodo supports only one license per record.")
            license_value = license_value[0]
        if license_value is not None:
            self.license = {"id": license_value}
        return self

    def add_publication_date(self):
        if "date-released" in self.cffobj.keys():
            self.publication_date = self.cffobj["date-released"]
        return self

    def add_upload_type(self):
        typ = self.cffobj.get("type", "")
        if typ == "dataset":
            self.upload_type = "dataset"
        elif typ == "software":
            self.upload_type = "software"
        else:
            # default value for type is 'software'
            self.upload_type = "software"
        return self
