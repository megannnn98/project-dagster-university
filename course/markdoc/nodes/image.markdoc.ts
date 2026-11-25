import {Tag, nodes} from '@markdoc/markdoc';

export const image = {
  render: 'img',
  attributes: nodes.image.attributes,
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    const {src} = attributes;
    const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
    const imageSrc =
      typeof src === 'string' && src.startsWith('/') && !src.startsWith('//')
        ? basePath + src
        : src;
    return new Tag('img', {...attributes, src: imageSrc}, node.transformChildren(config));
  },
};
