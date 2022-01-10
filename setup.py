#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-mosfilm.jarbasai=skill_mosfilm:MosfilmSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-mosfilm',
    version='0.0.1',
    description='ovos Mosfilm skill plugin',
    url='https://github.com/JarbasSkills/skill-mosfilm',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_mosfilm": ""},
    package_data={'skill_mosfilm': ['locale/*', 'ui/*']},
    packages=['skill_mosfilm'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
