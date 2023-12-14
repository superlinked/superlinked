# Superlinked Alpha (v1.7.1)

Notebook examples to show the common use-cases of the Superlinked framework. We have created notebooks for you to be able to run the experiments right in your ennvironment with direct access to your data.

## Usage

1. Create a token. ([see below](#create-a-token))
2. Import the [notebooks](./notebook/) in your preferred notebook environment.
3. Replace `YOUR_GITHUB_TOKEN` at the beginning of the notebook with your token to install the Superlinked framework.
4. Start experimenting.

> Tip: Make sure to keep your `pip install ...` script up-to-date with the latest version, if you are iterating on the notebooks.

## Reference

You can find a reference of the building blocks in the [docs](./docs/superlinked/framework) folder categorized by modules.

Some of the key components are:
1. [@schema](./docs/superlinked/framework/common/schema/schema.md): Define your schema classes.
2. [Space](./docs/superlinked/framework/dsl/space/index.md): Define embeddings on top of fields of one or more [schema](./docs/superlinked/framework/common/schema/schema_object.md) objects.
3. [Index](./docs/superlinked/framework/dsl/index/index.m.md): Organize your spaces into queriable indicies.
4. [Query](./docs/superlinked/framework/dsl/query/query.md): Define queries with parameters and weights.
5. [Source](./docs/superlinked/framework/dsl/source/index.md): Connect data sources to your schema.
6. [Parser](./docs/superlinked/framework/common/parser): Convenience tools to transform your data to schemas.  (e.g.: from [`pd.DataFrame`](./docs/superlinked/framework/common/parser/dataframe_parser.md))
7. [Executor](./docs/superlinked/framework/dsl/executor/in_memory/in_memory_executor.md): Run your configuration.

To learn more about the components and the use-cases we suggest to setup and check the examples in the [notebooks](./notebook/).

## Create a token

> You need to create a personal access token that is scoped to the superlinked-alpha project with the necessary permissions. 

1. Create a [new access token](https://github.com/settings/personal-access-tokens/new) on GitHub
1. Adjust the expiration date.
1. Select `superlinked` as the resource owner.
1. Select the `superlinked/superlinked-alpha` repository.
1. Provide read-only access on `Content` and `Metadata`.
1. Generate token.

![Create new access token](./asset/new_token.png)

## Contributing

If you encounter any challanges during your experiment, feel free to create an [issue](https://github.com/superlinked/superlinked-alpha/issues/new?assignees=kembala&labels=bug&projects=&template=bug_report.md&title=), request a [feature](https://github.com/superlinked/superlinked-alpha/issues/new?assignees=kembala&labels=enhancement&projects=&template=feature_request.md&title=) or to [start a discussion](https://github.com/superlinked/superlinked-alpha/discussions/new/choose).
Make sure to group your feedback in separate issues and discussions by topic. We are grateful for every and any feedback we can gather.