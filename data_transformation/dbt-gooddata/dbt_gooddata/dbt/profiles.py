import os
from typing import Optional
import attrs
import re
import yaml

from dbt_gooddata.dbt.base import Base


@attrs.define(auto_attribs=True, kw_only=True)
class DbtOutput(Base):
    name: str
    title: str
    type: str
    host: str
    port: str
    user: str
    password: str
    dbname: str
    schema: str


@attrs.define(auto_attribs=True, kw_only=True)
class DbtProfile(Base):
    name: str
    outputs: list[DbtOutput]


class DbtProfiles:
    def __init__(self, args):
        self.args = args
        with open(f"{args.profile_dir}/profiles.yml") as fp:
            self.dbt_profiles = yaml.safe_load(fp)

    @staticmethod
    def inject_password(output: DbtOutput):
        pwd_re = re.compile(r"env_var\('([^']+)'\)")
        if (pwd_match := pwd_re.search(output.password)) is not None:
            # print(f"DS PWD_MATCH={pwd_match.group(1)} PWD={os.getenv(pwd_match.group(1))}")
            output.password = os.getenv(pwd_match.group(1))
        # else do nothing, real password seems to be stored in dbt profile

    @property
    def profiles(self) -> list[DbtProfile]:
        profiles = []
        for profile, profile_def in self.dbt_profiles.items():
            outputs = []
            for output, output_def in profile_def["outputs"].items():
                dbt_output = DbtOutput.from_dict({"name": output} | output_def)
                self.inject_password(dbt_output)
                outputs.append(dbt_output)
            profiles.append(
                DbtProfile(name=profile, outputs=outputs)
            )
        return profiles

    @property
    def profile(self) -> Optional[DbtProfile]:
        for profile in self.profiles:
            if profile.name == self.args.profile:
                return profile

    @property
    def target(self) -> DbtOutput:
        for output in self.profile.outputs:
            if output.name == self.args.target:
                return output
